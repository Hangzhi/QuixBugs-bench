import pytest
from load_testdata import load_json_testcases

from test_utils import import_program

longest_common_subsequence = import_program('longest_common_subsequence')


testdata = load_json_testcases(longest_common_subsequence.__name__)


@pytest.mark.timeout(10)
@pytest.mark.parametrize("input_data,expected", testdata)
def test_longest_common_subsequence(input_data, expected):
    assert longest_common_subsequence(*input_data) == expected
