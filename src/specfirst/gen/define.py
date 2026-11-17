"""Define-XML v2.1 for the generated SDTM (PLAN.md section 6.4, stage S4).

One file describes the datasets of one study: every dataset, every
variable with its origin, the codelists with the terms the data hold, and
the methods of derived variables. The text is canonical: fixed order of
elements and attributes, and no clock.
"""

from __future__ import annotations

from xml.sax.saxutils import escape, quoteattr

from specfirst.gen import terms
from specfirst.gen.datasetjson import item_oid, text_length
from specfirst.gen.sdtm import DOMAINS, METHODS, ORDER, SDTMIG_VERSION, Variable

DEFINE_VERSION = "2.1.0"
_ORIGIN_SOURCE = {"Collected": "Investigator", "Derived": "Sponsor", "Assigned": "Sponsor",
                  "Protocol": "Sponsor"}
_DATA_TYPES = {"text": "text", "datetime": "partialDatetime", "integer": "integer",
               "float": "float"}
# Variables whose codelist is the adverse event dictionary of the study.
_DICTIONARY_CODED = ("AELLT", "AEDECOD", "AEHLT", "AEHLGT", "AEBODSYS", "AESOC")
# DSDECOD takes its terms from two CDISC codelists.
_DSDECOD_PARTS = ("NCOMPLT", "PROTMLST")


def _attributes(pairs: list[tuple[str, object]]) -> str:
    return "".join(f" {name}={quoteattr(str(value))}" for name, value in pairs
                   if value is not None)


def _text(tag: str, text: str, indent: str) -> list[str]:
    return [f"{indent}<{tag}>",
            f'{indent}  <TranslatedText xml:lang="en">{escape(text)}</TranslatedText>',
            f"{indent}</{tag}>"]


def _codelist_of(variable: Variable) -> str | None:
    if variable.name in _DICTIONARY_CODED:
        return "AEDICT"
    return variable.codelist


def _used(tables: dict[str, list[dict]], names: set[tuple[str, str]]) -> list[str]:
    values = {str(row[name]) for domain, name in names for row in tables.get(domain, [])
              if row[name] is not None}
    return sorted(values)


def _number_lengths(rows: list[dict], name: str) -> tuple[int, int]:
    """Length and significant digits of a float variable, from the values written."""
    texts = [repr(float(row[name])) for row in rows if row[name] is not None]
    length = max([len(t.rstrip("0").rstrip(".")) if "." in t else len(t) for t in texts],
                 default=1)
    digits = max([len(t.split(".")[1].rstrip("0")) for t in texts if "." in t], default=0)
    return max(length, 1), digits


def render(study: str, title: str, tables: dict[str, list[dict]], study_lists: dict[str, dict],
           stamp: str, system: dict, note: str) -> str:
    """The Define-XML text for the datasets in `tables`. `note` names what generated them."""
    present = [name for name in ORDER if name in tables]
    out: list[str] = ['<?xml version="1.0" encoding="UTF-8"?>']
    out.append("<ODM" + _attributes([
        ("xmlns", "http://www.cdisc.org/ns/odm/v1.3"),
        ("xmlns:def", "http://www.cdisc.org/ns/def/v2.1"),
        ("xmlns:xlink", "http://www.w3.org/1999/xlink"),
        ("FileType", "Snapshot"), ("FileOID", f"DEF.{study}.SDTM"), ("ODMVersion", "1.3.2"),
        ("CreationDateTime", stamp), ("Originator", system["name"]),
        ("SourceSystem", system["name"]), ("SourceSystemVersion", system["version"]),
        ("def:Context", "Other"),
    ]) + ">")
    out.append(f'  <Study OID="ST.{study}">')
    out.append("    <GlobalVariables>")
    out.append(f"      <StudyName>{escape(study)}</StudyName>")
    out.append(f"      <StudyDescription>{escape(title)}</StudyDescription>")
    out.append(f"      <ProtocolName>{escape(study)}</ProtocolName>")
    out.append("    </GlobalVariables>")
    out.append("    <MetaDataVersion" + _attributes([
        ("OID", f"MDV.{study}.SDTM"), ("Name", f"Study {study}, SDTM data definitions"),
        ("Description", note), ("def:DefineVersion", DEFINE_VERSION),
    ]) + ">")
    out.append("      <def:Standards>")
    out.append('        <def:Standard OID="STD.SDTMIG" Name="SDTMIG" Type="IG" '
               f'Version="{SDTMIG_VERSION}" Status="Final"/>')
    out.append('        <def:Standard OID="STD.CT.SDTM" Name="CDISC/NCI" Type="CT" '
               f'PublishingSet="SDTM" Version="{terms.CT_PACKAGE}" Status="Final"/>')
    out.append("      </def:Standards>")

    used_lists: dict[str, set[tuple[str, str]]] = {}
    used_methods: set[str] = set()
    items: list[str] = []
    for name in present:
        domain = DOMAINS[name]
        rows = tables[name]
        out.append("      <ItemGroupDef" + _attributes([
            ("OID", f"IG.{name}"), ("Name", name), ("Domain", name),
            ("Repeating", "Yes" if domain.repeating else "No"),
            ("IsReferenceData", "Yes" if domain.reference else "No"),
            ("SASDatasetName", name), ("Purpose", "Tabulation"),
            ("def:Structure", domain.structure), ("def:ArchiveLocationID", f"LF.{name}"),
            ("def:StandardOID", "STD.SDTMIG"),
        ]) + ">")
        out += _text("Description", domain.label, "        ")
        for order, variable in enumerate(domain.variables, start=1):
            key = domain.keys.index(variable.name) + 1 if variable.name in domain.keys else None
            if variable.method:
                used_methods.add(variable.method)
            empty = all(row[variable.name] is None for row in rows)
            out.append("        <ItemRef" + _attributes([
                ("ItemOID", item_oid(name, variable.name)), ("OrderNumber", order),
                ("Mandatory", "Yes" if variable.core == "Req" else "No"),
                ("KeySequence", key),
                ("MethodOID", f"MT.{variable.method}" if variable.method else None),
                ("def:HasNoData", "Yes" if empty else None),
            ]) + "/>")
            pairs: list[tuple[str, object]] = [
                ("OID", item_oid(name, variable.name)), ("Name", variable.name),
                ("DataType", _DATA_TYPES[variable.kind])]
            if variable.kind == "text":
                pairs.append(("Length", text_length(rows, variable.name)))
            elif variable.kind == "integer":
                pairs.append(("Length", max(
                    [len(str(int(r[variable.name]))) for r in rows
                     if r[variable.name] is not None], default=1)))
            elif variable.kind == "float":
                length, digits = _number_lengths(rows, variable.name)
                pairs += [("Length", length), ("SignificantDigits", digits)]
            pairs.append(("SASFieldName", variable.name))
            items.append("      <ItemDef" + _attributes(pairs) + ">")
            items += _text("Description", variable.label, "        ")
            codelist = _codelist_of(variable)
            if codelist:
                used_lists.setdefault(codelist, set()).add((name, variable.name))
                items.append(f'        <CodeListRef CodeListOID="CL.{codelist}"/>')
            items.append("        <def:Origin" + _attributes([
                ("Type", variable.origin), ("Source", _ORIGIN_SOURCE[variable.origin])]) + "/>")
            items.append("      </ItemDef>")
        out.append(f'        <def:Class Name="{domain.observation_class}"/>')
        out.append(f'        <def:leaf ID="LF.{name}" xlink:href="{name.lower()}.json">')
        out.append(f"          <def:title>{name.lower()}.json</def:title>")
        out.append("        </def:leaf>")
        out.append("      </ItemGroupDef>")
    out += items

    for codelist in sorted(used_lists):
        values = _used(tables, used_lists[codelist])
        if codelist == "AEDICT":
            out.append('      <CodeList OID="CL.AEDICT" Name="Adverse Event Dictionary" '
                       'DataType="text">')
            out.append("        <ExternalCodeList" + _attributes([
                ("Dictionary", terms.AE_DICTIONARY),
                ("Version", terms.AE_DICTIONARY_VERSION)]) + "/>")
            out.append("      </CodeList>")
            continue
        if codelist == "DSDECOD":
            known = {term: code for part in _DSDECOD_PARTS
                     for term, code in terms.CT[part]["terms"].items()}
            out.append('      <CodeList OID="CL.DSDECOD" Name="Standardized Disposition Term" '
                       'DataType="text" def:StandardOID="STD.CT.SDTM">')
            out += _enumerated(values, known)
            out.append("      </CodeList>")
            continue
        if codelist in terms.CT:
            standard = terms.CT[codelist]
            out.append("      <CodeList" + _attributes([
                ("OID", f"CL.{codelist}"), ("Name", standard["name"]), ("DataType", "text"),
                ("def:StandardOID", "STD.CT.SDTM")]) + ">")
            out += _enumerated(values, standard["terms"])
            out.append(f'        <Alias Context="nci:ExtCodeID" Name="{standard["code"]}"/>')
            out.append("      </CodeList>")
            continue
        study_list = study_lists[codelist]
        standard_oid = "STD.CT.SDTM" if study_list.get("nci") else None
        out.append("      <CodeList" + _attributes([
            ("OID", f"CL.{codelist}"), ("Name", study_list["label"]), ("DataType", "text"),
            ("def:StandardOID", standard_oid)]) + ">")
        if "decode" in study_list:
            for value in values:
                code = terms.TS_PARAMETERS.get(value, (None, None))[1] \
                    if codelist == "TSPARMCD" else None
                out.append(f"        <CodeListItem CodedValue={quoteattr(value)}>")
                out += _text("Decode", study_list["decode"].get(value, value), "          ")
                if code:
                    out.append(f'          <Alias Context="nci:ExtCodeID" Name="{code}"/>')
                out.append("        </CodeListItem>")
        else:
            codes = {name: code for name, code in terms.TS_PARAMETERS.values()} \
                if codelist == "TSPARM" else {}
            out += _enumerated(values, codes, extended=False)
        if study_list.get("nci"):
            out.append(f'        <Alias Context="nci:ExtCodeID" Name="{study_list["nci"]}"/>')
        out.append("      </CodeList>")

    for method in sorted(used_methods):
        out.append("      <MethodDef" + _attributes([
            ("OID", f"MT.{method}"), ("Name", f"Method {method}"), ("Type", "Computation"),
        ]) + ">")
        out += _text("Description", METHODS[method], "        ")
        out.append("      </MethodDef>")
    out.append("    </MetaDataVersion>")
    out.append("  </Study>")
    out.append("</ODM>")
    return "\n".join(out) + "\n"


def _enumerated(values: list[str], codes: dict[str, str], extended: bool = True) -> list[str]:
    """One EnumeratedItem per value; a value CDISC CT does not hold is an extended value."""
    lines = []
    for value in values:
        code = codes.get(value)
        extra = ' def:ExtendedValue="Yes"' if extended and code is None else ""
        if code:
            lines.append(f"        <EnumeratedItem CodedValue={quoteattr(value)}>")
            lines.append(f'          <Alias Context="nci:ExtCodeID" Name="{code}"/>')
            lines.append("        </EnumeratedItem>")
        else:
            lines.append(f"        <EnumeratedItem CodedValue={quoteattr(value)}{extra}/>")
    return lines
