import pytest
from load_testdata import load_json_testcases

from test_utils import import_program

mergesort = import_program('mergesort')


testdata = load_json_testcases(mergesort.__name__)


@pytest.mark.timeout(10)
@pytest.mark.parametrize("input_data,expected", testdata)
def test_mergesort(input_data, expected):
    assert mergesort(*input_data) == expected
