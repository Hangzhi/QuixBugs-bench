import pytest
from load_testdata import load_json_testcases

from test_utils import import_program

powerset = import_program('powerset')


testdata = load_json_testcases(powerset.__name__)


@pytest.mark.timeout(10)
@pytest.mark.parametrize("input_data,expected", testdata)
def test_powerset(input_data, expected):
    assert powerset(*input_data) == expected
