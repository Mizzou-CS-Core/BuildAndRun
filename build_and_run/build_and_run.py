import os
import re
from subprocess import DEVNULL, PIPE, run
from pathlib import Path


def compile(compilable_code_path: str, filename: str, use_makefile = False, output = "/a.out"):
    if use_makefile:
        result = run(["make"], stdout=DEVNULL, cwd=compilable_code_path)
    else:
        lab = f"{compilable_code_path}/{filename}" 
        result = run(["gcc", "-Wall", "-Werror", "-o", f"{compilable_code_path}{output}", lab])
    return True if result.returncode != 0 else False


def run_executable(path: str, executable_name = "a.out", execution_timeout = 5, input = None, run_valgrind = True, output_logs = False):
    errors = {}
    executable_path = Path(path) / executable_name
    output_log_path = Path(path) / "output.log"

    if not executable_path.is_file():
        errors['no_exe'] = "There was no executable."
        return errors
    print(executable_path)
    result = run(["stdbuf", "-oL", executable_path], timeout=execution_timeout,
                stdout=PIPE, stderr=PIPE, universal_newlines=True,
                input=input)
    if output_logs:
        with output_log_path.open('w') as log:
            log.write(result.stdout)
    else:
        print(result.stdout)
    if (result.returncode < 0):
        signum = -result.returncode
        if (signum == signal.SIGSEGV):
            errors["seg_fault"] = "Segmentation fault detected!"
    if run_valgrind:
        valgrind_log_path = Path(path) / "valgrind.log"
        stderr = run(["valgrind", executable_path], stdout=PIPE, stderr=PIPE, universal_newlines=True).stderr
        if re.search(r"[1-9]\d*\s+errors", stderr):
            errors["valgrind_errors"] = "Valgrind: There were errors in your program!"
        if not re.search("(All heap blocks were freed -- no leaks are possible)", stderr):
            errors["valgrind_memory_leak"] = "Valgrind: Memory leak detected!"
        if output_logs:
            with valgrind_log_path.open('w') as vg_log:
                vg_log.write(result.stderr)
    return errors

if __name__ == "__main__":
    compile(os.getcwd(), "test.c", False)
    errors = run_executable(executable_path=os.getcwd())
