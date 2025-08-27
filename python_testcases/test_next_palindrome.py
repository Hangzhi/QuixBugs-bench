import pytest
from load_testdata import load_json_testcases

from test_utils import import_program

next_palindrome = import_program('next_palindrome')


testdata = load_json_testcases(next_palindrome.__name__)


@pytest.mark.timeout(10)
@pytest.mark.parametrize("input_data,expected", testdata)
def test_next_palindrome(input_data, expected):
    assert next_palindrome(*input_data) == expected
