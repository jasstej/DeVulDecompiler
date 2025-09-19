import os
import sys
import tempfile
from typing import List

import angr
from angr.analyses import CFGFast, Decompiler
from angr.knowledge_plugins import Function

import warnings
warnings.filterwarnings('ignore')

def decompile():
    conts = sys.stdin.buffer.read()
    t = tempfile.NamedTemporaryFile()
    t.write(conts)
    t.flush()

    p = angr.Project(t.name, auto_load_libs=False, load_debug_info=False)
    cfg: CFGFast = p.analyses.CFGFast(
        normalize=True,
        resolve_indirect_jumps=True,
        data_references=True,
    )
    p.analyses.CompleteCallingConventions(
        cfg=cfg.model, recover_variables=True, analyze_callsites=True
    )

    # Optional function-level analysis controls
    only_func = os.getenv("ANGR_FUNCTION_NAME")
    limit_funcs = int(os.getenv("ANGR_MAX_FUNCTIONS", "0"))

    funcs: List[Function] = [
        func
        for func in cfg.functions.values()
        if not func.is_plt and not func.is_simprocedure and not func.is_alignment
    ]
    if only_func:
        funcs = [f for f in funcs if f.name == only_func]
        if not funcs:
            print(f"// No function named {only_func} found\n")
            return
    if limit_funcs > 0:
        funcs = funcs[:limit_funcs]

    for func in funcs:
        try:
            decompiler: Decompiler = p.analyses.Decompiler(func, cfg=cfg.model)

            if decompiler.codegen is None:
                print(f"// No decompilation output for function {func.name}\n")
                continue
            print(decompiler.codegen.text)
        except Exception as e:
            print(f"Exception thrown decompiling function {func.name}: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--version":
        print(angr.__version__)
        print("")  # No revision information known
        sys.exit(0)
    if len(sys.argv) > 1 and sys.argv[1] == "--name":
        print("angr")
        sys.exit(0)
    if len(sys.argv) > 1 and sys.argv[1] == "--url":
        print("https://angr.io/")
        sys.exit(0)

    decompile()
