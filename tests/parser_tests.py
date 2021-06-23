import unittest
from parsing.parse_program import *

class ParserTests(unittest.TestCase):

  def test_num_literals(self):
    self.assertEqual(
      parse_program("17"),
      ([], [Num(17)]))
    self.assertEqual(
      parse_program("-134.288"),
      ([], [Num(-134.288)]))
    self.assertEqual(
      parse_program("0"),
      ([], [Num(0)]))

  def test_add1(self):
    self.assertEqual(
      parse_program("(add1 7)"),
      ([], [Add1(Num(7))]))
    self.assertEqual(
      parse_program("(add1 -40)"),
      ([], [Add1(Num(-40))]))
    self.assertEqual(
      parse_program("(add1 (add1 (add1 301)))"),
      ([], [Add1(Add1(Add1(Num(301))))]))

  def test_sub1(self):
    self.assertEqual(
      parse_program("(sub1 13)"),
      ([], [Sub1(Num(13))]))
    self.assertEqual(
      parse_program("(sub1 -62)"),
      ([], [Sub1(Num(-62))]))
    self.assertEqual(
      parse_program("(sub1 (sub1 (sub1 16)))"),
      ([], [Sub1(Sub1(Sub1(Num(16))))]))

  def test_plus(self):
    self.assertEqual(
      parse_program("(+ 2 3)"),
      ([], [Plus(Num(2), Num(3))]))
    self.assertEqual(
      parse_program("(+ 0 -81.2)"),
      ([], [Plus(Num(0), Num(-81.2))]))
    self.assertEqual(
      parse_program("(+ (+ 4 4) (+ 17 -3))"),
      ([], [Plus(Plus(Num(4), Num(4)), Plus(Num(17), Num(-3)))]))

  def test_minus(self):
    self.assertEqual(
      parse_program("(- 40 16)"),
      ([], [Minus(Num(40), Num(16))]))
    self.assertEqual(
      parse_program("(- 17.3 -2)"),
      ([], [Minus(Num(17.3), Num(-2))]))
    self.assertEqual(
      parse_program("(- (- 7 2) (- -1 -5))"),
      ([], [Minus(Minus(Num(7), Num(2)), Minus(Num(-1), Num(-5)))]))

  def test_times(self):
    self.assertEqual(
      parse_program("(* 3 18)"),
      ([], [Times(Num(3), Num(18))]))
    self.assertEqual(
      parse_program("(* (* 4 3) (* 11 -17))"),
      ([], [Times(Times(Num(4), Num(3)), Times(Num(11), Num(-17)))]))

  def test_equals(self):
    self.assertEqual(
      parse_program("(= 300 200)"),
      ([], [Equals(Num(300), Num(200))]))
    self.assertEqual(
      parse_program("(= 0 -5)"),
      ([], [Equals(Num(0), Num(-5))]))

  def test_if(self):
    self.assertEqual(
      parse_program("(if 4 3 2)"),
      ([], [If(Num(4), Num(3), Num(2))]))
    self.assertEqual(
      parse_program("(if (= 2 1) (+ 1 2) (+ 2 3))"),
      ([], [If(Equals(Num(2), Num(1)), 
        Plus(Num(1), Num(2)), 
        Plus(Num(2), Num(3)))]))

  def test_let(self):
    self.assertEqual(
      parse_program("(let (x 2) x)"), 
      ([], [Let("x", Num(2), Name("x"))]))
    self.assertEqual(
      parse_program("(let (var-name (+ 1 2)) (sub1 var-name))"), 
      ([], [Let("var-name", Plus(Num(1), Num(2)), 
        Sub1(Name("var-name")))]))
    self.assertEqual(
      parse_program(
        "(let (y 3)" + \
          "(let (z 4)" + \
            "(+ z y)))"),
      ([], [Let("y", Num(3),
        Let("z", Num(4), Plus(Name("z"), Name("y"))))]))

  def test_app(self):
    self.assertEqual(
      parse_program("(fun 3 4)"),
      ([], [App("fun", [Num(3), Num(4)])]))
    self.assertEqual(
      parse_program("(no-args)"),
      ([], [App("no-args", [])]))
    self.assertEqual(
      parse_program("(many-args (+ 1 2) 3 4 5 6)"),
      ([], [App("many-args",
        [Plus(Num(1), Num(2)), Num(3), Num(4), Num(5), Num(6)])]))

  def test_names(self):
    self.assertEqual(
      parse_program("x"), 
      ([], [Name("x")]))
    self.assertEqual(
      parse_program("longer-name"), 
      ([], [Name("longer-name")]))
    self.assertEqual(
      parse_program("name!?-with-more-chars"), 
      ([], [Name("name!?-with-more-chars")]))

  def test_defns(self):
    self.assertEqual(
      parse_program("(def (f x y) (+ x y)) 3"),
      ([
        Defn("f", ["x", "y"], Plus(Name("x"), Name("y")))
      ], [Num(3)]))

    self.assertEqual(
      parse_program(
        "(def (fun1 a) a)\n" + \
        "(def (fun2 a b) b)\n" + \
        "(fun1 (fun2 4 5))"), 
      ([
        Defn("fun1", ["a"], Name("a")),
        Defn("fun2", ["a", "b"], Name("b")),
      ], [App("fun1", [App("fun2", [Num(4), Num(5)])])]))

    # program with no body is ok
    self.assertEqual(
      parse_program("(def (f x) x)"),
      ([Defn("f", ["x"], Name("x"))], []))
  
  def test_printexpr(self):
    self.assertEqual(
      parse_program("(print 10)"),
      ([], [PrintExpr(Num(10))]))
    self.assertEqual(
      parse_program("(print (print 1))"),
      ([], [PrintExpr(PrintExpr(Num(1)))]))

  def test_comments(self):
    self.assertEqual(
      parse_program("100 ; this is a comment"),
      ([], [Num(100)]))
    self.assertEqual(
      parse_program("; comment above function\n(def (f x) x)\n(f 2)"),
      ([Defn("f", ["x"], Name("x"))], [App("f", [Num(2)])]))

  def test_empty(self):
    self.assertEqual(
      parse_program(""),
      ([], []))

  def test_parse_errors(self):
    # body not last expression
    with self.assertRaises(ParseError):
      parse_program("(+ 1 2) (def (g x) x)")
    # invalid function name
    with self.assertRaises(ParseError):
      parse_program("(def (100 x) (+ x x))")
    # invalid identifier name in let
    with self.assertRaises(ParseError):
      parse_program("(let ((+ 2 3) 0) 1)")
    # invalid function name in application
    with self.assertRaises(ParseError):
      parse_program("(61 7 3 2)")
    # invalid expression (missing lparen)
    with self.assertRaises(ParseError):
      parse_program("def (f x) x)")
    # multiple definitions of same function
    with self.assertRaises(ParseError):
      parse_program("(def (f a) a) (def (g x) x) (def (f x) x) 10")
    # bad parameter names in defn
    with self.assertRaises(ParseError):
      parse_program("(def (f 1 2 3) (+ 1 2))")

  def test_lex_error(self):
    with self.assertRaises(LexError):
      parse_program("@*#&^%")
    with self.assertRaises(LexError):
      parse_program("~~_+;;-+_*##((")

if __name__ == '__main__':
  unittest.main()