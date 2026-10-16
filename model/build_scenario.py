#!/usr/bin/env python3
"""Rebuild the TRA_MS_ON_BAU_0 scenario database source from public TEMOA-Italy.

    python build_scenario.py path/to/TEMOA_Italy.sql  [-o TRA_MS_ON_BAU_0.sql]

The base file must be TEMOA-Italy release 3.3
(https://github.com/MAHTEP/TEMOA-Italy, tag 3.3, TEMOA-Italy/TEMOA_Italy.sql).

Steps
  1. apply base_edits.patch   -> rows of the base model that are disabled or re-valued
  2. insert modal_shift_additions.sql just before the Output_* table definitions
  3. check the result against the expected SHA-256

The output is the TRA_MS_ON_BAU_0 scenario of the report with the corrections listed
in README.md.
"""
import argparse, hashlib, pathlib, shutil, subprocess, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent
EXPECTED_SHA256 = "301d951be93983e5772d872a35d125ffcaed0ee8b27486147fc2767d4088cefc"
MARKER = 'CREATE TABLE "Output_'


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("base", type=pathlib.Path, help="TEMOA_Italy.sql from TEMOA-Italy release 3.3")
    ap.add_argument("-o", "--output", type=pathlib.Path, default=pathlib.Path("TRA_MS_ON_BAU_0.sql"))
    args = ap.parse_args()

    if shutil.which("patch") is None:
        sys.exit("the 'patch' utility is required (on Windows use Git Bash)")

    with tempfile.TemporaryDirectory() as tmp:
        patched = pathlib.Path(tmp) / "TEMOA_Italy.sql"
        shutil.copyfile(args.base, patched)
        res = subprocess.run(["patch", "--quiet", str(patched), str(HERE / "base_edits.patch")])
        if res.returncode != 0:
            sys.exit("base_edits.patch did not apply cleanly: is the base file release 3.3?")
        lines = patched.read_text(encoding="utf-8").split("\n")

    at = next((i for i, l in enumerate(lines) if l.startswith(MARKER)), None)
    if at is None:
        sys.exit("Output_* table definitions not found in the base file")
    additions = (HERE / "modal_shift_additions.sql").read_text(encoding="utf-8").split("\n")
    if additions and additions[-1] == "":
        additions.pop()
    out = "\n".join(lines[:at] + additions + lines[at:])
    args.output.write_text(out, encoding="utf-8", newline="")

    digest = hashlib.sha256(out.encode("utf-8")).hexdigest()
    status = "OK, matches the reference build" if digest == EXPECTED_SHA256 else "WARNING: differs from the reference build"
    print(f"{args.output}  ({out.count(chr(10)):,} lines)\nsha256 {digest}\n{status}")


if __name__ == "__main__":
    main()
