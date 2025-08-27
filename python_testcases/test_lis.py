import pytest
from load_testdata import load_json_testcases

from test_utils import import_program

lis = import_program('lis')


testdata = load_json_testcases(lis.__name__)


@pytest.mark.timeout(10)
@pytest.mark.parametrize("input_data,expected", testdata)
def test_lis(input_data, expected):
    assert lis(*input_data) == expected
