import pytest
from load_testdata import load_json_testcases

from test_utils import import_program

is_valid_parenthesization = import_program('is_valid_parenthesization')


testdata = load_json_testcases(is_valid_parenthesization.__name__)


@pytest.mark.timeout(10)
@pytest.mark.parametrize("input_data,expected", testdata)
def test_is_valid_parenthesization(input_data, expected):
    assert is_valid_parenthesization(*input_data) == expected
