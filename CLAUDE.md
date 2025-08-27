we need to benchmark the LLM agent on the performance of solving  the quixbugs and it will be used to compare the performance with terminal bench

folder structure 

- `python_programs`
- `correct_python_programs`
- `experiments_claude_code`
    - fixed_programs
        - program_1
    - `agent_log_claude.json`
    - `experiments_claude_code`_test_results.json
    - problem_solver_claude_code.py
    - ochestrater_claude_code.py

Preparation part 

- A dict
    - key: program_name
    - value: the number of test cases that should be passed
- 

problem_solver_claude_code

- Input
    - model_name
    - buggy_program_folder → absolute path
    - fixed_program_folder → absolute path
    - program_name
- Oracle
    - read the the buggy program
    - run the agent within the folder and try to fix the buggy program
    - place the fixed program in the `fixed_program_folder`
- Output
    - an `agent_log_claude.json` under the `fixed_program_folder`
        
        ```jsx
        "results": [
            "program": "bitcount",
            "success": false,
            "error": "Fixed file not created: experiments_claude_sdk/fixed_python_programs/bitcount.py",
            "claude_result": {
              "success": true,
              "result": null,
              "cost_usd": 0.1001232,
              "duration_ms": 24473,
              "num_turns": 5,
              "agent_output_preview": "{\"type\":\"system\",\"subtype\":\"init\",\"cwd\":\"/home/ubuntu/QuixBugs-bench\",\"session_id\":\"f3e5fc1a-c1cd-4054-bc5e-4044e278bb53\",\"tools\":[\"Task\",\"Bash\",\"Glob\",\"Grep\",\"LS\",\"ExitPlanMode\",\"Read\",\"Edit\",\"MultiE",
              "session_id": "306dff10-7989-4a7b-bce8-6d0862391db7"
            },
            "timestamp": "2025-08-27T01:50:57.910974"
          ],
        ```
        
    - a fixed program of {program_nam}.py in the fixed_program_folder

claude_code_problem_solver_ochestrator 

- copy the buggy program to the current folder
- run the program solver to
- clean up the unnecessary buggy programs

test_runner 

- input
    - program_folder
    - program_name
- Oracle
    - run the test first and
    - compare how many lines difference there are for `program_folder/program_name.py` and `python_programs/program_name.py`
- output
    - updated {program_folder_name}_test_results.json
        
        ```jsx
        {
          "metadata": {
            "model": "claude_code",
            "claude_model": null,
            "timestamp": "2025-08-27T01:15:20.367607",
            "total_programs": 1
          },
          "results": [
            {
              "program": "gcd",
              "test_status": "FAILED",
              "tests_passed": 0,
              "tests_failed": 0,
              "tests_skipped": 0,
              "is_one_line_change": true,
              "line_changes": 1,
              "timestamp": "2025-08-27T01:15:53.804726"
            }
          ],
        ```
        

test_result_scorer 

- TODO:
    - count how many test cases that have to be passed for each program.
- input
    - {program_folder_name}_test_results.json
- Oracle
    - One program is considered fully solved if
        - test_all_count = tests_passed + tests_skipped