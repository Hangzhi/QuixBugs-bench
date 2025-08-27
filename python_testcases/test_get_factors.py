import pytest
from load_testdata import load_json_testcases

from test_utils import import_program

get_factors = import_program('get_factors')


testdata = load_json_testcases(get_factors.__name__)


@pytest.mark.timeout(10)
@pytest.mark.parametrize("input_data,expected", testdata)
def test_get_factors(input_data, expected):
    assert get_factors(*input_data) == expected
