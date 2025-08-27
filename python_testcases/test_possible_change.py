import pytest
from load_testdata import load_json_testcases

from test_utils import import_program

possible_change = import_program('possible_change')


testdata = load_json_testcases(possible_change.__name__)


@pytest.mark.timeout(10)
@pytest.mark.parametrize("input_data,expected", testdata)
def test_possible_change(input_data, expected):
    assert possible_change(*input_data) == expected
