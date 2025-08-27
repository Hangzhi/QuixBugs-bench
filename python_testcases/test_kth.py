import pytest
from load_testdata import load_json_testcases

from test_utils import import_program

kth = import_program('kth')


testdata = load_json_testcases(kth.__name__)


@pytest.mark.timeout(10)
@pytest.mark.parametrize("input_data,expected", testdata)
def test_kth(input_data, expected):
    assert kth(*input_data) == expected
