import pytest
from load_testdata import load_json_testcases

from test_utils import import_program

quicksort = import_program('quicksort')


testdata = load_json_testcases(quicksort.__name__)


@pytest.mark.timeout(10)
@pytest.mark.parametrize("input_data,expected", testdata)
def test_quicksort(input_data, expected):
    assert quicksort(*input_data) == expected
