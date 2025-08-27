import pytest
from load_testdata import load_json_testcases

from test_utils import import_program

shunting_yard = import_program('shunting_yard')


testdata = load_json_testcases(shunting_yard.__name__)


@pytest.mark.timeout(10)
@pytest.mark.parametrize("input_data,expected", testdata)
def test_shunting_yard(input_data, expected):
    assert shunting_yard(*input_data) == expected
