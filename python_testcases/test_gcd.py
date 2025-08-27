import pytest
from load_testdata import load_json_testcases

from test_utils import import_program

gcd = import_program('gcd')


testdata = load_json_testcases(gcd.__name__)


@pytest.mark.timeout(10)
@pytest.mark.parametrize("input_data,expected", testdata)
def test_gcd(input_data, expected):
    assert gcd(*input_data) == expected
