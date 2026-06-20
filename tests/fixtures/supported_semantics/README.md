# Supported Semantics Fixture

This tracked fixture covers the currently supported formula translation and generation surface.

It should grow whenever Sheetforge adds support for a new formula function, operator, token form, or reference form. The purpose is to keep a durable synthetic convergence harness that can be rerun in any development environment without private workbooks.

The fixture intentionally stays small and non-private. Private workbook diagnostics decide the next implementation slice, but this fixture proves supported semantics remain translated and generated end to end.
