import pytest
from load_testdata import load_json_testcases

from test_utils import import_program

bitcount = import_program('bitcount')


testdata = load_json_testcases(bitcount.__name__)


@pytest.mark.timeout(10)
@pytest.mark.parametrize("input_data,expected", testdata)
def test_bitcount(input_data, expected):
    assert bitcount(*input_data) == expected
