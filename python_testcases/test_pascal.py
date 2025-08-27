import pytest
from load_testdata import load_json_testcases

from test_utils import import_program

pascal = import_program('pascal')


testdata = load_json_testcases(pascal.__name__)


@pytest.mark.timeout(10)
@pytest.mark.parametrize("input_data,expected", testdata)
def test_pascal(input_data, expected):
    assert pascal(*input_data) == expected
