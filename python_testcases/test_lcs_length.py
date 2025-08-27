import pytest
from load_testdata import load_json_testcases

from test_utils import import_program

lcs_length = import_program('lcs_length')


testdata = load_json_testcases(lcs_length.__name__)


@pytest.mark.timeout(10)
@pytest.mark.parametrize("input_data,expected", testdata)
def test_lcs_length(input_data, expected):
    assert lcs_length(*input_data) == expected
