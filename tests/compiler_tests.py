import unittest
from rasm.VirtualMachine import *
from compiler.compile import *
from parsing.parse_program import *

ENTRY_LABEL = "entry"

def compile_and_run(pgrm: str) -> float:
  """Compiles the given program and runs it to produce a number
  NOTE: does not catch exceptions, assumes tests will do so if intending"""
  # parse program to AST
  (defns, exprs) = parse_program(pgrm)
  # compile to rasm
  instrs = compile(defns, exprs)
  # execute on virtual machine (no printing)
  vm = VirtualMachine()
  vm.execute(instrs, suppress_output=True)
  # return computed answer
  return vm.rans

class CompilerTests(unittest.TestCase):

  def test_literals(self):
    self.assertEqual(
      compile_and_run("170"),
      170)
    self.assertEqual(
      compile_and_run("0"),
      0)
    self.assertEqual(
      compile_and_run("-8.3342"),
      -8.3342)

  def test_add1(self):
    self.assertEqual(
      compile_and_run("(add1 3)"),
      4)
    self.assertEqual(
      compile_and_run("(add1 (add1 (add1 40)))"),
      43)

  def test_sub1(self):
    self.assertEqual(
      compile_and_run("(sub1 -8)"),
      -9)
    self.assertEqual(
      compile_and_run("(sub1 (sub1 (sub1 (sub1 16))))"),
      12)

  def test_plus(self):
    self.assertEqual(
      compile_and_run("(+ 4 6)"),
      10)
    self.assertEqual(
      compile_and_run("(+ (+ 5 -3) (+ 30 8))"),
      40)
  
  def test_minus(self):
    self.assertEqual(
      compile_and_run("(- 9 14)"),
      -5)
    self.assertEqual(
      compile_and_run("(- (- 9 3) (- 3 2))"),
      5)

  def test_times(self):
    self.assertEqual(
      compile_and_run("(* 3 10)"),
      30)
    self.assertEqual(
      compile_and_run("(* 2 (* (* 8 10) (* 4 2)))"),
      1280)
    
  def test_equals(self):
    self.assertEqual(
      compile_and_run("(= 47 2)"),
      0)
    self.assertEqual(
      compile_and_run("(= 0 0)"),
      1)
    self.assertEqual(
      compile_and_run("(= -8 8)"),
      0)
    # conditions just evaluate to numbers so we can use them accordingly
    self.assertEqual(
      compile_and_run("(= (= 1 2) (= 4 7))"),
      1)
  
  def test_if(self):
    self.assertEqual(
      compile_and_run("(if 77 1 0)"), 1)
    self.assertEqual(
      compile_and_run("(if 0 1 0)"), 0)
    self.assertEqual(
      compile_and_run("(if -1 1 0)"), 1)
    self.assertEqual(
      compile_and_run("(if (= 4 5) (+ 2 3) (+ 4 5))"), 9)
    self.assertEqual(
      compile_and_run("(if (if 0 0 1) (if 4 5 2) (if 3 2 1))"), 5)

  def test_let_and_names(self):
    self.assertEqual(
      compile_and_run("(let (x 5) (add1 x))"), 6)
    self.assertEqual(
      compile_and_run("(let (name (+ 40 7)) (- name 3))"), 44)
    self.assertEqual(
      compile_and_run("""
        (let (x 5)
          (let (y 15)
            (let (z -1)
              (+ x (+ y z)))))"""), 
      19)

  def test_defns_and_app(self):
    self.assertEqual(
      compile_and_run("(def (f x) (+ x 2)) (f 7)"), 9)
    self.assertEqual(
      compile_and_run("(def (zero? n) (= n 0)) (if (zero? 5) 1 0)"), 0)
    self.assertEqual(
      compile_and_run("(def (sum a b c) (+ a (+ b c))) (sum 5 6 7)"), 18)
    self.assertEqual(
      compile_and_run("(def (const) (* 2 8)) (+ (const) (const))"),
      32)
    self.assertEqual(
      compile_and_run("(def (inc x) (add1 x)) (inc (inc (inc 5)))"),
      8)

    # recursive functions
    self.assertEqual(
      compile_and_run("""
        (def (fact n)
          (if (= n 0) 1 (* n (fact (sub1 n)))))
        (fact 5)"""),
      120)
    self.assertEqual(
      compile_and_run("""
        (def (odd n) (if (= n 0) 0 (even (sub1 n))))
        (def (even n) (if (= n 0) 1 (odd (sub1 n))))
        (even 16)"""),
      1)

    # infinite loop (causes stack overflow)
    with self.assertRaises(InvalidRsp):
      compile_and_run("""
        (def (loop) (loop))
        (loop)""")

    # functions can call each other
    self.assertEqual(
      compile_and_run("""
        (def (f x) (+ x x))
        (def (g x) (* (f x) 3))
        (def (h x) (add1 (g (sub1 x))))
        (def (i x) (+ (f x) (h x)))
        (i 4)
      """),
      27)

  def test_print(self):
    # print evaluates to its operand
    self.assertEqual(
      compile_and_run("(print (+ 2 10))"), 
      12)
    self.assertEqual(
      compile_and_run("(print (print (print 3)))"),
      3)

  def test_empty_program(self):
    # empty program generates no code (other than entry label),
    # so rans stays at initial value (0)
    self.assertEqual(compile_and_run(""), 0)

  def test_arity_mismatch(self):
    with self.assertRaises(ArityMismatch):
      compile_and_run("(def (f x y) (* x y)) (f 10)")
    with self.assertRaises(ArityMismatch):
      compile_and_run("(def (g) (+ 2 3)) (g 17 1 0 4)")
    with self.assertRaises(ArityMismatch):
      compile_and_run("""
        (def (args a1 a2 a3 a4 a5 a6 a7 a8 a9 a10) 0) 
        (args 1 2 3 4 5 6 7 8 9)""")

  def test_undefined_fun(self):
    with self.assertRaises(UndefinedFun):
      compile_and_run("(def (g x) x) (f 5)")
    with self.assertRaises(UndefinedFun):
      compile_and_run("(let (fun 11) (fun 0 1 2))")

  def test_unbound_name(self):
    with self.assertRaises(UnboundName):
      compile_and_run("x")
    with self.assertRaises(UnboundName):
      compile_and_run("(def (f x) x) f")
    with self.assertRaises(UnboundName):
      compile_and_run("(+ 2 name)")

if __name__ == '__main__':
  unittest.main()