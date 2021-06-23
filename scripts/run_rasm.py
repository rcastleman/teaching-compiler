import sys
import argparse
from rasm.VirtualMachine import *
from parsing.parse_rasm import *
from parsing.Parser import ParseError
from parsing.Lexer import LexError
from .util import *

argparser = argparse.ArgumentParser(description="Run a rasm file")
argparser.add_argument(
  'file', type=str, nargs=1, help='a rasm file to run')

args = argparser.parse_args()
filename = args.file[0]

try:
  file = open(filename, "r")
  pgrm = file.read()

  try:
    instrs = parse_rasm(pgrm)
    vm = VirtualMachine()
    vm.execute(instrs)
  except (LexError, ParseError, VMError) as err:
    print(err)
  except Exception as err:
    print(f"InternalError: {err}")
except FileNotFoundError:
  print(f"{filename} not found")