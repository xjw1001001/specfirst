"""The vocabulary of generated studies.

Controlled terms are the submission values of CDISC Controlled Terminology
for SDTM; the gate checks them with CDISC CORE. Everything else is invented
for this generator: no term list of a real study is used.

The adverse event dictionary below is NOT MedDRA. MedDRA needs a license,
so the generator carries a small dictionary of its own: common event names
in five levels with made-up codes. Define-XML names it as the dictionary of
the coded adverse event variables.
"""

from __future__ import annotations

AE_DICTIONARY = "SPECFIRST EVENT TERMS"
AE_DICTIONARY_VERSION = "1"

# Body system -> preferred terms. Each term: (name, weight, grows with dose).
_BODY_SYSTEMS: tuple[tuple[str, tuple[tuple[str, float, bool], ...]], ...] = (
    ("Gastrointestinal disorders", (
        ("Nausea", 5.0, True), ("Diarrhea", 4.0, True), ("Vomiting", 2.0, True),
        ("Abdominal pain", 2.0, False), ("Constipation", 1.5, False), ("Dry mouth", 1.5, True))),
    ("Nervous system disorders", (
        ("Headache", 6.0, False), ("Dizziness", 4.0, True), ("Somnolence", 2.0, True),
        ("Tremor", 0.8, True))),
    ("General disorders", (
        ("Fatigue", 4.0, True), ("Fever", 1.5, False), ("Peripheral swelling", 1.0, False),
        ("Chest discomfort", 0.6, False))),
    ("Infections", (
        ("Common cold", 4.0, False), ("Urinary tract infection", 1.5, False),
        ("Sinus infection", 1.2, False), ("Influenza", 1.0, False))),
    ("Skin disorders", (
        ("Rash", 2.0, True), ("Itching", 1.5, True), ("Dry skin", 0.8, False))),
    ("Musculoskeletal disorders", (
        ("Back pain", 2.5, False), ("Joint pain", 2.0, False), ("Muscle cramp", 1.2, False))),
    ("Respiratory disorders", (
        ("Cough", 2.5, False), ("Sore throat", 1.5, False), ("Shortness of breath", 0.7, False))),
    ("Cardiac disorders", (
        ("Palpitations", 1.0, True), ("Slow heart rate", 0.5, True))),
    ("Psychiatric disorders", (
        ("Insomnia", 2.0, False), ("Anxiety", 1.2, False))),
)


def ae_terms() -> list[dict]:
    """The dictionary as rows: one per preferred term, with all five levels and their codes."""
    rows = []
    term_number = 0
    for system_number, (system, terms) in enumerate(_BODY_SYSTEMS, start=1):
        stem = system.replace(" disorders", "")
        for name, weight, dose_related in terms:
            term_number += 1
            rows.append({
                "soc": system, "soc_code": 100 + system_number,
                "hlgt": f"{stem} conditions", "hlgt_code": 200 + system_number,
                "hlt": f"{stem} signs and symptoms", "hlt_code": 300 + system_number,
                "pt": name, "pt_code": 1000 + term_number,
                "llt": name, "llt_code": 5000 + term_number,
                "weight": weight, "dose_related": dose_related,
            })
    return rows


# Vital sign tests: code, name, unit (CDISC CT: VSTESTCD, VSTEST, UNIT), decimals,
# mean and standard deviation of the simple model, change per dose step.
VITAL_SIGNS: dict[str, dict] = {
    "SYSBP": {"test": "Systolic Blood Pressure", "unit": "mmHg", "decimals": 0,
              "mean": 132.0, "sd": 12.0, "within": 6.0, "dose_effect": -3.0},
    "DIABP": {"test": "Diastolic Blood Pressure", "unit": "mmHg", "decimals": 0,
              "mean": 82.0, "sd": 8.0, "within": 5.0, "dose_effect": -1.5},
    "PULSE": {"test": "Pulse Rate", "unit": "beats/min", "decimals": 0,
              "mean": 72.0, "sd": 9.0, "within": 5.0, "dose_effect": 0.5},
    "WEIGHT": {"test": "Weight", "unit": "kg", "decimals": 1,
               "mean": 78.0, "sd": 14.0, "within": 0.8, "dose_effect": -0.2},
    "HEIGHT": {"test": "Height", "unit": "cm", "decimals": 0,
               "mean": 170.0, "sd": 9.0, "within": 0.0, "dose_effect": 0.0},
    "TEMP": {"test": "Temperature", "unit": "C", "decimals": 1,
             "mean": 36.6, "sd": 0.3, "within": 0.25, "dose_effect": 0.0},
}

CAUSALITY_SCALES: dict[str, tuple[str, ...]] = {
    # The last value is the strongest relation; the first means no relation.
    "five": ("NOT RELATED", "UNLIKELY RELATED", "POSSIBLY RELATED", "PROBABLY RELATED",
             "RELATED"),
    "four": ("NONE", "REMOTE", "POSSIBLE", "PROBABLE"),
    "two": ("NOT RELATED", "RELATED"),
}

SEVERITIES = ("MILD", "MODERATE", "SEVERE")
RACES = ("WHITE", "BLACK OR AFRICAN AMERICAN", "ASIAN", "AMERICAN INDIAN OR ALASKA NATIVE",
         "NATIVE HAWAIIAN OR OTHER PACIFIC ISLANDER", "OTHER")
RACE_WEIGHTS = (70.0, 14.0, 9.0, 1.5, 0.5, 5.0)
ETHNICITIES = ("NOT HISPANIC OR LATINO", "HISPANIC OR LATINO")
ETHNICITY_WEIGHTS = (85.0, 15.0)
COUNTRIES = ("USA", "CAN", "DEU", "GBR", "POL", "ESP")

# Reasons for early discontinuation (CDISC CT, codelist NCOMPLT) with weights.
DISCONTINUATION_REASONS = (
    ("ADVERSE EVENT", 35.0), ("WITHDRAWAL BY SUBJECT", 30.0), ("LOST TO FOLLOW-UP", 15.0),
    ("PHYSICIAN DECISION", 10.0), ("LACK OF EFFICACY", 10.0),
)

# CDISC Controlled Terminology for SDTM, package of 2025-09-26: the codelists
# and terms the generator writes, with their NCI codes (for Define-XML). It is
# the last package that still has the codelists RACE and ETHNIC that SDTMIG 3.4
# names. Codelist name -> NCI code, long name, extensible, term -> NCI code.
CT_PACKAGE = "2025-09-26"
CT: dict[str, dict] = {
    "SEX": {"code": "C66731", "name": "Sex", "extensible": False,
            "terms": {"F": "C16576", "M": "C20197"}},
    "RACE": {"code": "C74457", "name": "Race", "extensible": False,
             "terms": {"WHITE": "C41261", "BLACK OR AFRICAN AMERICAN": "C16352",
                       "ASIAN": "C41260", "AMERICAN INDIAN OR ALASKA NATIVE": "C41259",
                       "NATIVE HAWAIIAN OR OTHER PACIFIC ISLANDER": "C41219",
                       "OTHER": "C17649"}},
    "ETHNIC": {"code": "C66790", "name": "Ethnic Group", "extensible": False,
               "terms": {"NOT HISPANIC OR LATINO": "C41222", "HISPANIC OR LATINO": "C17459"}},
    "AGEU": {"code": "C66781", "name": "Age Unit", "extensible": False,
             "terms": {"YEARS": "C29848"}},
    "ARMNULRS": {"code": "C142179", "name": "Arm Null Reason", "extensible": True,
                 "terms": {"SCREEN FAILURE": "C49628", "NOT ASSIGNED": "C142239",
                           "ASSIGNED, NOT TREATED": "C142238",
                           "UNPLANNED TREATMENT": "C142240"}},
    "NY": {"code": "C66742", "name": "No Yes Response", "extensible": False,
           "terms": {"N": "C49487", "Y": "C49488"}},
    "EPOCH": {"code": "C99079", "name": "Epoch", "extensible": True,
              "terms": {"SCREENING": "C202487", "TREATMENT": "C101526",
                        "FOLLOW-UP": "C202578"}},
    "DSCAT": {"code": "C74558", "name": "Category of Disposition Event", "extensible": False,
              "terms": {"DISPOSITION EVENT": "C74590", "PROTOCOL MILESTONE": "C74588"}},
    "DSSCAT": {"code": "C170443", "name": "Subcategory for Disposition Event",
               "extensible": True,
               "terms": {"STUDY PARTICIPATION": "C170569", "STUDY TREATMENT": "C170570"}},
    "NCOMPLT": {"code": "C66727", "name": "Completion/Reason for Non-Completion",
                "extensible": True,
                "terms": {"COMPLETED": "C25250", "ADVERSE EVENT": "C41331", "DEATH": "C28554",
                          "LOST TO FOLLOW-UP": "C48227", "PHYSICIAN DECISION": "C48250",
                          "WITHDRAWAL BY SUBJECT": "C49634", "SCREEN FAILURE": "C49628",
                          "LACK OF EFFICACY": "C48226"}},
    "PROTMLST": {"code": "C114118", "name": "Protocol Milestone", "extensible": True,
                 "terms": {"INFORMED CONSENT OBTAINED": "C16735", "RANDOMIZED": "C114209"}},
    "ACN": {"code": "C66767", "name": "Action Taken with Study Treatment", "extensible": False,
            "terms": {"DOSE NOT CHANGED": "C49504", "DRUG INTERRUPTED": "C49501",
                      "DRUG WITHDRAWN": "C49502", "NOT APPLICABLE": "C48660"}},
    "OUT": {"code": "C66768", "name": "Outcome of Event", "extensible": False,
            "terms": {"FATAL": "C48275", "NOT RECOVERED/NOT RESOLVED": "C49494",
                      "RECOVERED/RESOLVED": "C49498"}},
    "AESEV": {"code": "C66769", "name": "Severity/Intensity Scale for Adverse Events",
              "extensible": False,
              "terms": {"MILD": "C41338", "MODERATE": "C41339", "SEVERE": "C41340"}},
    "UNIT": {"code": "C71620", "name": "Unit", "extensible": True,
             "terms": {"mg": "C28253"}},
    "FRM": {"code": "C66726", "name": "Dosage Form", "extensible": True,
            "terms": {"TABLET": "C42998"}},
    "FREQ": {"code": "C71113", "name": "Frequency", "extensible": True,
             "terms": {"QD": "C25473"}},
    "ROUTE": {"code": "C66729", "name": "Route of Administration Response",
              "extensible": True, "terms": {"ORAL": "C38288"}},
    "VSTESTCD": {"code": "C66741", "name": "Vital Signs Test Code", "extensible": True,
                 "terms": {"SYSBP": "C25298", "DIABP": "C25299", "PULSE": "C49676",
                           "WEIGHT": "C25208", "HEIGHT": "C25347", "TEMP": "C174446"}},
    "VSTEST": {"code": "C67153", "name": "Vital Signs Test Name", "extensible": True,
               "terms": {"Systolic Blood Pressure": "C25298",
                         "Diastolic Blood Pressure": "C25299", "Pulse Rate": "C49676",
                         "Weight": "C25208", "Height": "C25347", "Temperature": "C174446"}},
    "VSRESU": {"code": "C66770", "name": "Units for Vital Signs Results", "extensible": True,
               "terms": {"mmHg": "C49670", "beats/min": "C49673", "kg": "C28252",
                         "cm": "C49668", "C": "C42559"}},
    "POSITION": {"code": "C71148", "name": "Position", "extensible": True,
                 "terms": {"SITTING": "C62122"}},
}

# Trial summary parameters (CDISC CT, codelists TSPARMCD and TSPARM): code -> name, NCI code.
TS_PARAMETERS: dict[str, tuple[str, str]] = {
    "ACTSUB": ("Actual Number of Subjects", "C98703"),
    "ADAPT": ("Adaptive Design", "C146995"),
    "ADDON": ("Added on to Existing Treatments", "C49703"),
    "AGEMAX": ("Planned Maximum Age of Subjects", "C49694"),
    "AGEMIN": ("Planned Minimum Age of Subjects", "C49693"),
    "DOSE": ("Dose per Administration", "C25488"),
    "DOSFRQ": ("Dosing Frequency", "C89081"),
    "DOSU": ("Dose Units", "C73558"),
    "HLTSUBJI": ("Healthy Subject Indicator", "C98737"),
    "INTMODEL": ("Intervention Model", "C98746"),
    "INTTYPE": ("Intervention Type", "C98747"),
    "LENGTH": ("Trial Length", "C49697"),
    "NARMS": ("Planned Number of Arms", "C98771"),
    "PLANSUB": ("Planned Number of Subjects", "C49692"),
    "RANDOM": ("Trial is Randomized", "C25196"),
    "ROUTE": ("Route of Administration", "C38114"),
    "SDTIGVER": ("SDTM IG Version", "C156604"),
    "SDTMVER": ("SDTM Version", "C156605"),
    "SENDTC": ("Study End Date", "C90462"),
    "SEXPOP": ("Sex of Participants", "C49696"),
    "SPONSOR": ("Clinical Study Sponsor", "C70793"),
    "SSTDTC": ("Study Start Date", "C69208"),
    "STYPE": ("Study Type", "C142175"),
    "TBLIND": ("Trial Blinding Schema", "C49658"),
    "TCNTRL": ("Control Type", "C49647"),
    "TITLE": ("Trial Title", "C49802"),
    "TPHASE": ("Trial Phase Classification", "C48281"),
    "TRT": ("Investigational Therapy or Treatment", "C41161"),
    "TTYPE": ("Trial Type", "C49660"),
}
