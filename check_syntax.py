import os
import py_compile

for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            try:
                py_compile.compile(path, doraise=True)
                print(f"[OK] {path}")
            except py_compile.PyCompileError as e:
                print(f"[ERROR] {path}")
                print(e)
