import os
import sys
import traceback
from typing_extensions import Optional, Dict, Any, List


def run_code(code: str):
    import sys
    import traceback

    # Use a copy of the current globals
    exec_globals = globals().copy()  # Copy to prevent modifications to actual globals

    exec_locals = {}

    try:
        exec(code, exec_globals, exec_locals)
        # Merge exec_globals and exec_locals if needed
        return {**exec_globals, **exec_locals}
    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback_str = "".join(
            traceback.format_exception(exc_type, exc_value, exc_traceback)
        )
        raise Exception(f"Code execution failed:\n{traceback_str}")
