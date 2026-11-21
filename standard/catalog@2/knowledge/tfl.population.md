# Which analysis set does the output use? (`tfl.population`)

The analysis set fixes which subjects the table counts and the number in each column header.
The answer is given once per table family.

## Where it is stated

- SAP: the section of each analysis ("demographics will be summarized for the ... set"), the
  section on analysis sets, and the title or subtitle line of each table shell.
- Protocol: statistical section, in general words.
- Usually stated for safety tables; for demographics it varies between studies.

## Words to look for

- `safety`: "safety population", "safety analysis set", "all treated subjects".
- `randomized`: "intent-to-treat population", "full analysis set", "all randomized subjects",
  "randomized set".
- `efficacy`: "efficacy-evaluable set", "evaluable population", when it is the set that
  `pop.efficacy.rule` defines.
- A protocol written to ICH M11 says "participant" for subject and "study intervention" for
  study treatment; read them as the same words.

## Traps

- Map the name through the SAP's own definitions, not by the name alone: a "full analysis
  set" is all randomized subjects in one study and a narrower set in another.
- Demographics are often shown on several sets. Take the set of the main demographics table;
  if the text names several and no main one, report the passage.
- If a shell subtitle and the SAP text disagree, cite both passages in the answer.
- "All enrolled" or "all screened" subjects match no alternative; report the passage.
- For the demographics table, the pilot CSR (Table 14-2.01) and ICH E3 section 11.2 use the
  randomized set; the FDA guide's Table 2, the ARS example's demographics analyses
  (AnalysisSet_02_SAF) and cardinal's Table 2 use the safety set. A house may take either;
  its house standard says which.
- Silent documents: the house default depends on the table family; take the default of the
  output's family and cite the house standard.
