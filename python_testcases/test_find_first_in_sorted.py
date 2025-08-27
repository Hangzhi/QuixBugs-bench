import pytest
from load_testdata import load_json_testcases

from test_utils import import_program

find_first_in_sorted = import_program('find_first_in_sorted')


testdata = load_json_testcases(find_first_in_sorted.__name__)


@pytest.mark.timeout(10)
@pytest.mark.parametrize("input_data,expected", testdata)
def test_find_first_in_sorted(input_data, expected):
    assert find_first_in_sorted(*input_data) == expected
