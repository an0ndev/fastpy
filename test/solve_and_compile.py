import ast
import os
import pathlib
import timeit
from fastpy.constants import SPACER
import fastpy.context
import fastpy.compiler
test_file_name = "target"
loops = 1
test_file_src = f"{test_file_name}.py"
test_file_mid = f"{test_file_name}.cpp"
tmp_dir = "tmp"
with open (test_file_src, "r") as test_file:
    test_file_contents = test_file.read ()

print ("SOURCE:")
print (SPACER)
print (test_file_contents)
time_result = timeit.timeit (lambda: os.system (f"python3 {test_file_src}"), number = loops)
print ("\n")
print (f"{loops} run(s) took {time_result}s")
print (SPACER, end = "\n" * 2)

module = ast.parse (test_file_contents, filename = test_file_name)
ctx = fastpy.context.Context (module, is_main = True)
solved = ctx.solve ()
if not os.path.exists ("tmp"): os.mkdir ("tmp")
if not os.path.exists ("tmp/src"): os.mkdir ("tmp/src")
with open ("tmp/src/target.cpp", "w+") as target_mid_out_file: target_mid_out_file.write (solved)

print ()
print ("RESULT:")
print (SPACER)
print (solved)
print (SPACER)

compiler = fastpy.compiler.Compiler (pathlib.Path ("tmp"), test_file_name)
compiler.compile ()

print ("Compiled successfully!", end = "\n\n")
print ("PROGRAM OUTPUT:")
print (SPACER)
time_result = timeit.timeit (compiler.run, number = loops)
print ("\n")
print (f"{loops} run(s) took {time_result}s")