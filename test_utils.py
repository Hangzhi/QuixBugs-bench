import importlib
import pytest


def import_program(program_name):
    """
    Dynamically import a program based on the configured folder.
    Uses pytest.program_folder if set, otherwise falls back to default behavior.
    """
    if pytest.use_correct:
        module_path = f"correct_python_programs.{program_name}"
    else:
        folder = getattr(pytest, 'program_folder', 'python_programs')
        module_path = f"{folder}.{program_name}"
    
    module = importlib.import_module(module_path)
    return getattr(module, program_name)