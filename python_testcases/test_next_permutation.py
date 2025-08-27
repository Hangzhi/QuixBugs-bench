import pytest
from load_testdata import load_json_testcases

from test_utils import import_program

next_permutation = import_program('next_permutation')


testdata = load_json_testcases(next_permutation.__name__)


@pytest.mark.timeout(10)
@pytest.mark.parametrize("input_data,expected", testdata)
def test_next_permutation(input_data, expected):
    assert next_permutation(*input_data) == expected
