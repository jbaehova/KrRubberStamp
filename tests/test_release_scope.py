"""Public authored commands stop at the final two-batch project boundary."""

import pytest

from KrRubberStamp import cli
from scripts import build_authored_catalog


@pytest.mark.parametrize("batch", [3, 4])
@pytest.mark.parametrize(
    "arguments", [["build-authored", "--batch"], ["export-hf", "--batch"], ["export-hf", "--upto"]]
)
def test_public_cli_rejects_unrequested_batches(arguments, batch):
    with pytest.raises(SystemExit) as error:
        cli.main([*arguments, str(batch)])
    assert error.value.code == 2


@pytest.mark.parametrize("option", ["--batch", "--upto"])
@pytest.mark.parametrize("batch", [3, 4])
def test_catalog_rejects_unrequested_batches_without_writing(option, batch):
    with pytest.raises(SystemExit) as error:
        build_authored_catalog.main([option, str(batch)])
    assert error.value.code == 2
