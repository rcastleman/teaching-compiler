import sys
import argparse
from .util import *
from parsing.parse_program import *
from rasm.VirtualMachine import *
from compiler.Errors import *
from compiler.compile import compile as student_compile
from demo.compile import compile as demo_compile

argparser = argparse.ArgumentParser(description="Compile a file")
argparser.add_argument(
  'file', type=str, nargs=1, help='a file to compile')
argparser.add_argument(
  '-r', '--run', 
  help='run the compiled program & print answer',
  action='store_true')
argparser.add_argument(
  '-s', '--rasm',
  help='write the generated rasm to a file')
argparser.add_argument(
  '-d', '--demo', 
  help='compile using the demo implementation',
  action='store_true')

args = argparser.parse_args()
filename = args.file[0]

try:
  # open program file for reading
  file = open(filename, "r")
  pgrm = file.read()

  try:
    # parse defns and body
    (defns, exprs) = parse_program(pgrm)

    # compile program to rasm
    if args.demo:
      instrs = demo_compile(defns, exprs)
    else:
      instrs = student_compile(defns, exprs)

    # if requested, output generated rasm
    if args.rasm:
      try:
        file = open(args.rasm, "w+")
        for ins in instrs:
          file.write(str(ins) + '\n')
      except Exception as err:
        print(f"error with rasm file: {err}")

    # if requested, run program
    if args.run:
      vm = VirtualMachine()
      vm.execute(instrs)
  except (LexError, ParseError, CompileError, VMError) as err:
    print(err)
  except NotImplementedError as err:
    print(f"NotImplementedError: {err}")
  except Exception as err:
    print(f"InternalError: {err}")
except FileNotFoundError:
  print(f"file not found: {filename}")