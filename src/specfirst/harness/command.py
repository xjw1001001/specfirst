"""`specfirst run ...` and `specfirst ask ...`: the harness from the command line
(PLAN.md sections 11.1 to 11.3 and 12; docs/decisions/ADR-010.md).

    specfirst run task KIT [--stage C|T] [--condition notes|catalog] [--tasks DIR]
    specfirst run arm KIT --arm S|R|C [--stage] [--condition] [--tasks DIR] [--runs DIR]
                  [--seed TEXT | --seed-file FILE] [--stub PLAN] [--score] [--keep]
    specfirst run probe KIT [--tasks DIR] [--runs DIR]
    specfirst run check KEPT --kit KIT [--tasks DIR] [--seed TEXT] [--score]
    specfirst run score RUN --kit KIT
    specfirst run skills [--write]
    specfirst run validate --run RUN --task TASK            (what bin/check runs)
    specfirst run pilot --arm S|R --folder DIR [--condition] [--tasks DIR] [--runs DIR]
                  [--score]                                 (CDISCPILOT01, stage T)
    specfirst ask "<question>" --decision ID [--unit UNIT] --run RUN --task TASK

The folders of tasks and runs lie outside every checkout: `--tasks` and
`--runs`, or SPECFIRST_TASKS and SPECFIRST_RUNS. The reader of arm R is the
program SPECFIRST_READER names (default `claude`); `--stub PLAN` runs the
stub reader with that plan instead. `--keep` copies the run into
src/specfirst/harness/kept, as the gate reads it.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from specfirst.compile import catalog as catalogs
from specfirst.gen import natural
from specfirst.harness import adapter, knowledge, oracle, outputs, runs
from specfirst.harness import task as tasks


def _folder(given: str | None, variable: str) -> Path:
    named = given or os.environ.get(variable)
    if not named:
        raise SystemExit(f"specfirst run: give the folder (--{variable.split('_')[1].lower()} "
                         f"or {variable}); it lies outside every checkout")
    return Path(named)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="specfirst run", description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="what", required=True)
    p_task = commands.add_parser("task", help="write the task folder of a kit")
    p_arm = commands.add_parser("arm", help="run an arm on a kit")
    p_probe = commands.add_parser("probe", help="the isolation probe of the reader")
    for sub in (p_task, p_arm, p_probe):
        sub.add_argument("kit", help="a kit folder")
        sub.add_argument("--stage", choices=tasks.STAGES, default="C")
        sub.add_argument("--condition", choices=tasks.CONDITIONS, default="notes")
        sub.add_argument("--tasks", help="the folder of task folders (SPECFIRST_TASKS)")
    for sub in (p_arm, p_probe):
        sub.add_argument("--runs", help="the folder of run folders (SPECFIRST_RUNS)")
    p_arm.add_argument("--arm", choices=runs.ARMS, required=True)
    p_arm.add_argument("--seed", help="the seed of the kit, as text (a canary)")
    p_arm.add_argument("--seed-file", help="a file outside the checkout that holds the seed")
    p_arm.add_argument("--stub", help="run the stub reader with this plan (a JSON file)")
    p_arm.add_argument("--score", action="store_true", help="score the run on its kit")
    p_arm.add_argument("--keep", action="store_true",
                       help="copy the run into src/specfirst/harness/kept")
    p_check = commands.add_parser("check", help="check a kept run against its kit")
    p_check.add_argument("kept", help="a folder of src/specfirst/harness/kept")
    p_check.add_argument("--kit", required=True)
    p_check.add_argument("--tasks")
    p_check.add_argument("--seed")
    p_check.add_argument("--score", action="store_true")
    p_score = commands.add_parser("score", help="score a run on its kit")
    p_score.add_argument("folder", help="a run folder or a kept run")
    p_score.add_argument("--kit", required=True)
    p_skills = commands.add_parser("skills", help="check the skills; --write renders the notes")
    p_skills.add_argument("--write", action="store_true")
    p_validate = commands.add_parser("validate", help="the problems of the files in out/")
    p_validate.add_argument("--run", required=True)
    p_validate.add_argument("--task", required=True)
    p_pilot = commands.add_parser("pilot", help="run arm S or R on the pilot, stage T "
                                  "(ADR-005, decision 5; report only)")
    p_pilot.add_argument("--arm", choices=("S", "R"), required=True)
    p_pilot.add_argument("--folder", required=True, help="where the pilot folder is written, "
                         "outside every checkout (third-party material)")
    p_pilot.add_argument("--condition", choices=tasks.CONDITIONS, default="notes")
    p_pilot.add_argument("--tasks", help="the folder of task folders (SPECFIRST_TASKS)")
    p_pilot.add_argument("--runs", help="the folder of run folders (SPECFIRST_RUNS)")
    p_pilot.add_argument("--score", action="store_true", help="the pilot report of the run")
    return parser


def _seed(args: argparse.Namespace) -> tuple[str | None, Path | None]:
    if args.seed_file:
        path = Path(args.seed_file)
        if tasks.inside_checkout(path) is not None:
            raise SystemExit("specfirst run: the seed file must lie outside every checkout")
        return path.read_text(encoding="utf-8").strip(), path
    return args.seed, None


def validate(root: Path, run_dir: Path, task_dir: Path) -> int:
    told = json.loads((run_dir / runs.TASK_JSON).read_text(encoding="ascii"))
    catalog = catalogs.load(catalogs.default_dir(root))
    found = outputs.problems(task_dir / tasks.OUT, catalog,
                             tuple(tuple(key) for key in told["keys"]),
                             outputs.task_documents(task_dir), oracle.read_asks(run_dir))
    for problem in found:
        print(problem)
    print(f"out/: {len(found)} problems" if found else "out/: no problem")
    return 1 if found else 0


def main(root: Path, argv: list[str]) -> int:
    args = build_parser().parse_args(argv)
    if args.what == "skills":
        if args.write:
            for path in knowledge.write(root):
                print(f"wrote {path.relative_to(root).as_posix()}")
        found = knowledge.problems(root, [], knowledge.store_paragraphs(natural.store_dir()))
        print("\n".join(found) if found else "skills: rendered, Agent Skill format, no leak "
              "of the store")
        return 1 if found else 0
    if args.what == "validate":
        return validate(root, Path(args.run), Path(args.task))
    if args.what == "task":
        made = tasks.build(root, Path(args.kit), _folder(args.tasks, "SPECFIRST_TASKS"),
                           args.stage, args.condition)
        print(f"task {made.id}: {made.folder}, {len(made.manifest)} files, "
              f"{len(made.keys)} decisions of {', '.join(made.units)}")
        problems = tasks.problems(made.folder, Path(args.kit))
        print("\n".join(problems) if problems else "holds only what a reader may see")
        return 1 if problems else 0
    if args.what == "score":
        print("\n".join(runs.score(root, Path(args.kit), Path(args.folder))))
        return 0
    if args.what == "check":
        found, hits, _ = runs.check(root, Path(args.kept), Path(args.kit),
                                    _folder(args.tasks, "SPECFIRST_TASKS"), args.seed)
        for line in found + [hit.line() for hit in hits]:
            print(line)
        print(f"kept run {Path(args.kept).name}: "
              + ("PASS" if not (found or hits) else "FAIL"))
        if args.score:
            print("\n".join(runs.score(root, Path(args.kit), Path(args.kept))))
        return 1 if found or hits else 0
    tasks_dir = _folder(args.tasks, "SPECFIRST_TASKS")
    runs_dir = _folder(args.runs, "SPECFIRST_RUNS")
    if args.what == "pilot":
        from specfirst.harness import pilot

        try:
            folder = pilot.write(root, Path(args.folder))
        except pilot.PilotTaskError as error:
            print(f"pilot: {error}")
            return 2
        print(f"pilot folder: {folder}")
        made = runs.run(root, folder, args.arm, tasks_dir, runs_dir, "T", args.condition)
        print("\n".join(runs.lines(made)))
        if args.score:
            try:
                print("\n".join(pilot.score(root, made.folder)))
            except pilot.PilotTaskError as error:
                print(f"pilot: {error}")
                return 1
        return 0 if made.passed else 1
    if args.what == "probe":
        made, found = runs.probe(root, Path(args.kit), tasks_dir, runs_dir)
        print("\n".join(runs.lines(made)))
        print("\n".join(found) if found else "every attempt was denied; the scan is clean")
        print(f"PROBE: {'FAIL' if found else 'PASS'}")
        return 1 if found else 0
    seed, seed_file = _seed(args)
    reader, env = None, None
    if args.stub:
        reader = adapter.stub_reader()
        env = {"SPECFIRST_STUB_PLAN": str(Path(args.stub).resolve())}
    made = runs.run(root, Path(args.kit), args.arm, tasks_dir, runs_dir, args.stage,
                    args.condition, reader, seed, seed_file, env=env)
    print("\n".join(runs.lines(made)))
    if args.keep:
        task_dir = tasks_dir / made.record["task"]["id"]
        print(f"kept in {runs.keep(made, task_dir, Path(args.kit), root)}")
    if args.score:
        print("\n".join(runs.score(root, Path(args.kit), made.folder)))
    return 0 if made.passed else 1


def ask_main(root: Path, argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="specfirst ask",
                                     description="ask about one decision (PLAN.md 11.3)")
    parser.add_argument("question")
    parser.add_argument("--decision", required=True)
    parser.add_argument("--unit")
    parser.add_argument("--run", required=True)
    parser.add_argument("--task", required=True)
    args = parser.parse_args(argv)
    catalog = catalogs.load(catalogs.default_dir(root))
    text, _ = oracle.ask(catalog, Path(args.run), Path(args.task), args.decision,
                         args.question, args.unit)
    print(text)
    return 0


if __name__ == "__main__":  # pragma: no cover
    from specfirst.paths import repo_root

    sys.exit(main(repo_root(), sys.argv[1:]))
