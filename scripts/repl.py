import signal
import sys
import argparse
from .util import *
from parsing.parse_program import *
from rasm.VirtualMachine import *
from compiler.Errors import *
from compiler.compile import compile as student_compile
from demo.compile import compile as demo_compile

argparser = argparse.ArgumentParser(description="Launch a repl")
argparser.add_argument(
  '-d', '--demo', 
  help='launch a repl using the demo implementation',
  action='store_true')
args = argparser.parse_args()

def quit_handler(sig, frame):
  """Quit from the REPL on receipt of a signal"""
  print("\nExiting REPL")
  sys.exit(0)

def launch_repl(compile):
  """Creates a REPL which reads input from stdin, parses/compiles/runs, 
  then prints the resulting value. Generic over what compile function
  to use so we can launch with both student/demo implementations"""
  # handle SIGINT by exiting gracefully
  signal.signal(signal.SIGINT, quit_handler)

  running_defns = []
  vm = VirtualMachine()

  # REPL loop
  while True:
    pgrm = input("> ")
    try:
      (defns, exprs) = parse_program(pgrm)

      # skip empty input
      if len(defns + exprs) == 0:
        continue

      # defn names in our running list so far
      defn_names = list(map(lambda d: d.name, running_defns))
      for d in defns:
        if d.name in defn_names:
          raise ParseError(f"function '{d.name}' has multiple definitions")
        else:
          # do this so duplicate defns in the same repl input are caught
          defn_names.append(d.name)

      # add defns to running list
      running_defns += defns

      # if expression(s) entered, compile/run them with current defns
      if len(exprs) > 0:
        instrs = compile(running_defns, exprs)
        vm.execute(instrs)
        print_num(vm.rans)
    except (LexError, ParseError, CompileError, VMError) as err:
      print(err)
    except NotImplementedError as err:
      print(f"NotImplementedError: {err}")
    except Exception as err:
      print(f"InternalError: {err}")

# if args.demo then use the demo implementation
if args.demo:
  launch_repl(demo_compile)
else:
  launch_repl(student_compile)