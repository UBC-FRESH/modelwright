import sheetforge


def test_package_imports() -> None:
    assert sheetforge.__version__ == "0.1.0a1"
