import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--correct", action="store_true", help="run tests on the correct version"
    )
    parser.addoption("--runslow", action="store_true", help="run slow tests")
    parser.addoption(
        "--program-folder", 
        default="python_programs",
        help="specify the folder containing programs to test (default: python_programs)"
    )


def pytest_configure(config):
    pytest.use_correct = config.getoption("--correct")
    pytest.run_slow = config.getoption("--runslow")
    pytest.program_folder = config.getoption("--program-folder")
