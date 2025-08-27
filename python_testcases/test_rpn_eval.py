import pytest
from load_testdata import load_json_testcases

from test_utils import import_program

rpn_eval = import_program('rpn_eval')


testdata = load_json_testcases(rpn_eval.__name__)


@pytest.mark.timeout(10)
@pytest.mark.parametrize("input_data,expected", testdata)
def test_rpn_eval(input_data, expected):
    assert rpn_eval(*input_data) == expected
