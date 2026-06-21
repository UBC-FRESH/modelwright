# Tests

Tests should use tracked synthetic fixtures or fixture builders, and should write generated workbooks, generated Python, IR JSON, and validation reports to pytest temporary directories.

`tests/fixtures/supported_semantics/` is the durable harness for currently supported formula/operator/token semantics. Expand it whenever Modelwright adds support for new spreadsheet semantics.

Do not add private workbooks, bulky generated artifacts, or ignored `tmp/` outputs to this directory.
