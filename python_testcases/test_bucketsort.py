import pytest
from load_testdata import load_json_testcases

from test_utils import import_program

bucketsort = import_program('bucketsort')


testdata = load_json_testcases(bucketsort.__name__)


@pytest.mark.timeout(10)
@pytest.mark.parametrize("input_data,expected", testdata)
def test_bucketsort(input_data, expected):
    assert bucketsort(*input_data) == expected
