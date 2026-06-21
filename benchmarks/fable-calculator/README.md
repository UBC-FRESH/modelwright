# FABLE Calculator External Benchmarks

This directory tracks reproducible benchmark metadata for the public FABLE Calculator workbooks.

The workbook binaries are intentionally not committed to this repository. They are public benchmark inputs, but keeping them external avoids redistributing binary workbook files and keeps the Git history light.

## Source

Download folder:

```text
https://www.dropbox.com/scl/fo/ndgldfnq81v794mm8yebe/ADusMz23xtmYKDXoEkiNtJM?rlkey=d87qhjf5zd0pcowd5pfl5qdu7&st=qijm4tta&e=2&dl=0
```

## Local Placement

Recommended command from the repository root:

```bash
scripts/bootstrap_dev_env.sh --benchmarks
```

The script downloads the Dropbox folder as a ZIP, finds each expected workbook by checksum, and copies it
to the canonical ignored path. If Dropbox or network access is awkward in a development environment,
download the folder ZIP manually and run:

```bash
.venv/bin/python scripts/materialize_fable_benchmarks.py --from-zip path/to/downloaded-folder.zip
```

If the files are already extracted somewhere, run:

```bash
.venv/bin/python scripts/materialize_fable_benchmarks.py --from-dir path/to/extracted-folder
```

The canonical local workbook directory is:

```text
tmp/private-workbooks/
```

Expected local files:

```text
tmp/private-workbooks/2019_Open_FABLECalculator.xlsx
tmp/private-workbooks/2020_Open_FABLECalculator.xlsx
tmp/private-workbooks/2021_Open_FABLECalculator.xlsx
```

## Benchmark Roles

- `2019_Open_FABLECalculator.xlsx`: broken-reference regression. This file contains explicit source `#REF!` references and should verify that Modelwright reports source workbook defects without silently generating normal Python behavior.
- `2020_Open_FABLECalculator.xlsx`: primary benchmark. This is the current main real-workbook benchmark for conversion planning and generated-model scope work.
- `2021_Open_FABLECalculator.xlsx`: stress benchmark. Use after the 2020 benchmark is stable.

## Verification

After downloading, verify file checksums from the repository root:

```bash
sha256sum -c benchmarks/fable-calculator/checksums.sha256
```

The checksum file uses paths under `tmp/private-workbooks/`, so it verifies the local ignored copies without tracking the workbook binaries.

## Default CI

These benchmarks are not part of default CI. They are large real-workbook benchmarks and should be run only in explicit benchmark or local evaluation workflows.
