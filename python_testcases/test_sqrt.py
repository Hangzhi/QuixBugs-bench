import pytest
from load_testdata import load_json_testcases

from test_utils import import_program

sqrt = import_program('sqrt')


testdata = load_json_testcases(sqrt.__name__)


@pytest.mark.timeout(10)
@pytest.mark.parametrize("input_data,expected", testdata)
def test_sqrt(input_data, expected):
    assert sqrt(*input_data) == pytest.approx(expected, abs=input_data[-1])
