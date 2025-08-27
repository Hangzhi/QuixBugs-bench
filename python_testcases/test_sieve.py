import pytest
from load_testdata import load_json_testcases

from test_utils import import_program

sieve = import_program('sieve')


testdata = load_json_testcases(sieve.__name__)


@pytest.mark.timeout(10)
@pytest.mark.parametrize("input_data,expected", testdata)
def test_sieve(input_data, expected):
    assert sieve(*input_data) == expected
