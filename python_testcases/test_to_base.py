import pytest
from load_testdata import load_json_testcases

from test_utils import import_program

to_base = import_program('to_base')


testdata = load_json_testcases(to_base.__name__)


@pytest.mark.timeout(10)
@pytest.mark.parametrize("input_data,expected", testdata)
def test_to_base(input_data, expected):
    assert to_base(*input_data) == expected
