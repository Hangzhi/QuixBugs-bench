import pytest
from load_testdata import load_json_testcases

from test_utils import import_program

max_sublist_sum = import_program('max_sublist_sum')


testdata = load_json_testcases(max_sublist_sum.__name__)


@pytest.mark.timeout(10)
@pytest.mark.parametrize("input_data,expected", testdata)
def test_max_sublist_sum(input_data, expected):
    assert max_sublist_sum(*input_data) == expected
