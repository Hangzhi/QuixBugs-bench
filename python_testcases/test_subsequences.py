import pytest
from load_testdata import load_json_testcases

from test_utils import import_program

subsequences = import_program('subsequences')


testdata = load_json_testcases(subsequences.__name__)


@pytest.mark.timeout(10)
@pytest.mark.parametrize("input_data,expected", testdata)
def test_subsequences(input_data, expected):
    assert subsequences(*input_data) == expected
