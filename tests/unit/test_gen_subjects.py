"""The subject process and the SDTM written from it (PLAN.md section 6.4, stages S2 and S4)."""

from __future__ import annotations

import datetime

import pyarrow.parquet as pq
import pytest

from specfirst.compile import catalog as catalogs
from specfirst.gen import GENERATOR, datasetjson, pgfix, sdtm, study, subjects
from specfirst.gen import design as designs
from specfirst.gen.rng import Stream

SEED = "test-subjects"


@pytest.fixture(scope="module")
def catalog(root):
    return catalogs.load(catalogs.default_dir(root))


@pytest.fixture(scope="module")
def design(catalog):
    return pgfix.sample(SEED, study.catalog_label(catalog))


@pytest.fixture(scope="module")
def people(design):
    ctx = subjects.Context.of(design)
    found = subjects.base_subjects(ctx, Stream(SEED, "base"))
    subjects.assign_identifiers(design, found)
    return found


def test_every_arm_gets_exactly_its_planned_number(design, people):
    for arm in designs.arms(design):
        randomized = [s for s in people if s.planned_arm == arm["name"]]
        assert len(randomized) == arm["plannedNumber"]
        # In the base process a randomized subject is dosed with the planned treatment.
        assert all(s.actual_arm == s.planned_arm and s.first_dose for s in randomized)
    failures = [s for s in people if s.state == "screen_failure"]
    assert failures and all(s.planned_arm is None and not s.doses for s in failures)


def test_the_process_is_a_function_of_design_and_seed(design):
    ctx = subjects.Context.of(design)
    first = [subjects.as_record(s) for s in subjects.base_subjects(ctx, Stream(SEED, "base"))]
    again = [subjects.as_record(s) for s in subjects.base_subjects(ctx, Stream(SEED, "base"))]
    other = [subjects.as_record(s) for s in subjects.base_subjects(ctx, Stream("else", "base"))]
    assert first == again and first != other


def test_the_dates_of_a_subject_are_in_order(design, people):
    start = datetime.date.fromisoformat(design["study"]["startDate"])
    planned = designs.treatment_days(design)
    for s in people:
        assert start <= s.consent <= s.end_of_study
        if s.first_dose is None:
            continue
        assert s.consent < s.first_dose <= s.last_dose <= s.end_of_study
        assert (s.last_dose - s.first_dose).days + 1 <= planned + 8
        ordered = sorted(s.doses, key=lambda d: d.start)
        assert ordered[0].start == s.first_dose and ordered[0].start_time
        assert ordered[-1].end == s.last_dose
        for before, after in zip(ordered, ordered[1:], strict=False):
            assert before.end + subjects.DAY == after.start  # no gap, no overlap
        for event in s.events:
            assert event.end is None or event.start <= event.end
            assert event.start >= s.consent
        # Base events either end before the first dose or start after its day.
        assert all(e.start > s.first_dose or (e.end and e.end < s.first_dose) for e in s.events)
        # No base event starts after the last dose: such events come from probes.
        assert all(e.start <= s.last_dose for e in s.events)


def test_a_death_ends_everything(design):
    ctx = subjects.Context.of(design)
    found = []
    for number in range(40):
        found += subjects.base_subjects(ctx, Stream(f"deaths-{number}", "base"))
        dead = [s for s in found if s.death]
        if dead:
            break
    assert dead, "no fatal event in 40 studies: the model lost its deaths"
    for s in dead:
        assert s.end_of_study == s.death and s.last_dose <= s.death
        assert all(v.date <= s.death for v in s.visits)
        assert [d.decod for d in s.dispositions if d.category == "DISPOSITION EVENT"] == ["DEATH"]
        assert sum(e.fatal for e in s.events) == 1


def test_no_subject_of_the_spared_arm_dies(design):
    ctx = subjects.Context.of(design)
    for number in range(15):
        found = subjects.base_subjects(ctx, Stream(f"spared-{number}", "base"), spared="PBO")
        assert not any(s.death for s in found if s.planned_arm == "PBO")


def test_identifiers_are_unique_and_follow_the_consent(design, people):
    assert len({s.usubjid for s in people}) == len(people)
    assert [s.usubjid for s in people] == sorted(s.usubjid for s in people)
    study_id = designs.study_id(design)
    for s in people:
        assert s.usubjid == f"{study_id}-{s.subjid}" and s.subjid.startswith(s.site + "-")
    by_site: dict[str, list] = {}
    for s in people:
        by_site.setdefault(s.site, []).append(s)
    for members in by_site.values():
        assert [m.consent for m in members] == sorted(m.consent for m in members)


@pytest.fixture(scope="module")
def tables(design, people):
    return sdtm.build(design, people)


def test_every_row_has_every_variable_of_its_domain(tables):
    assert list(tables) == list(sdtm.ORDER)
    for name, rows in tables.items():
        names = [v.name for v in sdtm.DOMAINS[name].variables]
        assert rows, name
        assert all(list(row) == names for row in rows)
        assert all(row["DOMAIN"] == name for row in rows)
        for variable in sdtm.DOMAINS[name].variables:
            if variable.core == "Req":
                assert all(row[variable.name] is not None for row in rows), variable.name


def test_keys_are_unique_and_sequence_numbers_count_from_one(tables):
    for name, rows in tables.items():
        domain = sdtm.DOMAINS[name]
        keys = [tuple(row[key] for key in domain.keys) for row in rows]
        if name != "VS":  # the natural key of VS is not unique for repeated measurements
            assert len(set(keys)) == len(keys), name
        seq = f"{name}SEQ"
        if seq in rows[0] and "USUBJID" in rows[0]:
            per_subject: dict[str, list[int]] = {}
            for row in rows:
                per_subject.setdefault(row["USUBJID"], []).append(row[seq])
            assert all(numbers == list(range(1, len(numbers) + 1))
                       for numbers in per_subject.values()), name


def test_dm_follows_sdtmig_3_4_for_subjects_without_an_arm(design, people, tables):
    by_subject = {row["USUBJID"]: row for row in tables["DM"]}
    assert len(by_subject) == len(people)
    for s in people:
        row = by_subject[s.usubjid]
        if s.state == "screen_failure":
            assert (row["ARMCD"], row["ARM"], row["ACTARMCD"]) == (None, None, None)
            assert row["ARMNRS"] == "SCREEN FAILURE" and row["RFSTDTC"] is None
        else:
            arm = designs.arm(design, s.planned_arm)
            assert (row["ARMCD"], row["ARM"]) == (arm["name"], arm["description"])
            assert row["ARMNRS"] is None
            assert row["RFSTDTC"] == s.first_dose.isoformat()
            assert row["RFXSTDTC"] == f"{s.first_dose.isoformat()}T{s.first_dose_time}"
            assert row["RFXENDTC"] == row["RFENDTC"] == s.last_dose.isoformat()
        assert row["DTHFL"] == ("Y" if s.death else None)
    # The values SCRNFAIL and NOTASSGN of earlier SDTMIG versions are never written.
    assert not {row["ARMCD"] for row in tables["DM"]} & {"SCRNFAIL", "NOTASSGN"}


def test_study_days_have_no_day_zero(tables):
    assert sdtm.study_day("2021-03-10", "2021-03-10") == 1
    assert sdtm.study_day("2021-03-09", "2021-03-10") == -1
    assert sdtm.study_day("2021-03-12T08:00", "2021-03-10") == 3
    assert sdtm.study_day("2021-03", "2021-03-10") is None
    assert sdtm.study_day("2021-03-12", None) is None
    days = [row["AESTDY"] for row in tables["AE"] if row["AESTDY"] is not None]
    assert days and 0 not in days


def test_what_the_house_specs_rely_on(design, tables):
    """docs/state/std.md, 'For other tracks': the conventions of the SDTM that the specs read."""
    read = {
        "DM": ["ARM", "ARMCD", "ACTARM", "RFSTDTC", "RFXSTDTC", "AGE", "AGEU", "SEX", "RACE",
               "ETHNIC", "SUBJID", "SITEID"],
        "EX": ["EXSEQ", "EXTRT", "EXDOSE", "EXSTDTC", "EXENDTC"],
        "DS": ["DSSEQ", "DSCAT", "DSSCAT", "DSDECOD", "DSSTDTC"],
        "SV": ["VISIT", "VISITNUM"],
        "VS": ["VSSEQ", "VSTESTCD", "VSTEST", "VSSTRESN", "VSDTC", "VISIT", "VISITNUM",
               "VISITDY"],
        "AE": ["AESEQ", "AETERM", "AEDECOD", "AESOC", "AESEV", "AESER", "AEREL", "AEACN",
               "AEOUT", "AESDTH", "AESTDTC", "AEENDTC"],
    }
    for name, variables in read.items():
        assert set(variables) <= set(tables[name][0]), name
    placebo = [row for row in tables["EX"] if row["EXDOSE"] == 0]
    assert placebo and all("PLACEBO" in row["EXTRT"] for row in placebo)
    assert all("PLACEBO" not in row["EXTRT"] for row in tables["EX"] if row["EXDOSE"] > 0)
    assert all(row["VISITDY"] is not None for row in tables["VS"])  # no unscheduled visit yet
    assert {row["DSCAT"] for row in tables["DS"]} == {"DISPOSITION EVENT", "PROTOCOL MILESTONE"}
    scale = set(design["collection"]["adverseEvents"]["causality"])
    assert {row["AEREL"] for row in tables["AE"]} <= scale


def test_controlled_terms_are_terms_of_the_table(tables):
    from specfirst.gen import terms

    for name, rows in tables.items():
        for variable in sdtm.DOMAINS[name].variables:
            if variable.codelist in terms.CT:
                allowed = set(terms.CT[variable.codelist]["terms"])
                used = {row[variable.name] for row in rows} - {None}
                assert used <= allowed, (name, variable.name, sorted(used - allowed))
    decods = {row["DSDECOD"] for row in tables["DS"]}
    assert decods <= set(terms.CT["NCOMPLT"]["terms"]) | set(terms.CT["PROTMLST"]["terms"])


def test_the_dictionary_is_ours_and_complete():
    from specfirst.gen import terms

    rows = terms.ae_terms()
    assert len({row["pt"] for row in rows}) == len(rows) >= 30
    assert len({row["pt_code"] for row in rows}) == len(rows)
    assert all(row[key] for row in rows for key in ("soc", "hlgt", "hlt", "pt", "llt"))
    assert terms.AE_DICTIONARY != "MedDRA"


def test_parquet_and_dataset_json_hold_the_same_rows(design, tables, people, tmp_path):
    label = "specfirst-m1 test"
    study.write_dataset(tmp_path, design, tables, label, study.data_stamp(people))
    for name, rows in tables.items():
        names, read_back = datasetjson.read_rows(tmp_path / f"{name.lower()}.json")
        assert names == [v.name for v in sdtm.DOMAINS[name].variables]
        table = pq.read_table(tmp_path / f"{name.lower()}.parquet")
        assert table.column_names == names
        assert table.to_pylist() == read_back == rows, name
        note = table.schema.metadata[b"specfirst"].decode("ascii")
        assert GENERATOR in note and label in note
    text = (tmp_path / "define.xml").read_text(encoding="ascii")
    assert f"for the catalog {label}" in text and 'def:DefineVersion="2.1.0"' in text
    for name in tables:
        assert f'<ItemGroupDef OID="IG.{name}"' in text
    assert text.count("<ItemDef ") == sum(len(sdtm.DOMAINS[n].variables) for n in tables)
    assert 'def:HasNoData="Yes"' in text  # ACTARMUD holds no value
    # Text files carry no clock: the stamp is the last date of the study.
    stamp = study.data_stamp(people)
    assert f'CreationDateTime="{stamp}"' in text
    assert max(s.end_of_study for s in people).isoformat() in stamp


def test_a_domain_list_limits_what_is_written(design, people):
    limited = sdtm.build(design, people, ("DM", "AE"))
    assert list(limited) == ["DM", "AE"]
