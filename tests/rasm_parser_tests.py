import unittest
from parsing.parse_rasm import *

class RasmParserTests(unittest.TestCase):

  def test_labels(self):
    self.assertEqual(
      parse_rasm("this_is_a_label:"),
      [Label("this_is_a_label")])
    self.assertEqual(
      parse_rasm("a:"),
      [Label("a")])

  def test_mov(self):
    self.assertEqual(
      parse_rasm("mov 10, rans"),
      [Mov(Imm(10), Rans())])
    self.assertEqual(
      parse_rasm("mov rsp, rans"),
      [Mov(Rsp(), Rans())])
    self.assertEqual(
      parse_rasm("mov [rsp + 2], [rsp + 8]"),
      [Mov(StackOff(2), StackOff(8))])
  
  def test_add(self):
    self.assertEqual(
      parse_rasm("add 17, rsp"),
      [Add(Imm(17), Rsp())])
    self.assertEqual(
      parse_rasm("add rsp, rsp"),
      [Add(Rsp(), Rsp())])
    self.assertEqual(
      parse_rasm("add [rsp + 0], [rsp + 2]"),
      [Add(StackOff(0), StackOff(2))])

  def test_sub(self):
    self.assertEqual(
      parse_rasm("sub 300, rans"),
      [Sub(Imm(300), Rans())])
    self.assertEqual(
      parse_rasm("sub rsp, rans"),
      [Sub(Rsp(), Rans())])
    self.assertEqual(
      parse_rasm("sub [rsp + 5], [rsp + 9]"),
      [Sub(StackOff(5), StackOff(9))])

  def test_mul(self):
    self.assertEqual(
      parse_rasm("mul 62, rans"),
      [Mul(Imm(62), Rans())])
    self.assertEqual(
      parse_rasm("mul rsp, rans"),
      [Mul(Rsp(), Rans())])
    self.assertEqual(
      parse_rasm("mul [rsp + 3], [rsp + 1]"),
      [Mul(StackOff(3), StackOff(1))])

  def test_cmp(self):
    self.assertEqual(
      parse_rasm("cmp 10, 3"),
      [Cmp(Imm(10), Imm(3))])
    self.assertEqual(
      parse_rasm("cmp rans, rsp"),
      [Cmp(Rans(), Rsp())])
    self.assertEqual(
      parse_rasm("cmp [rsp + 100], [rsp + 17]"),
      [Cmp(StackOff(100), StackOff(17))])

  def test_jmp(self):
    self.assertEqual(
      parse_rasm("jmp target_name"),
      [Jmp("target_name")])
    self.assertEqual(
      parse_rasm("jmp lbl123"),
      [Jmp("lbl123")])

  def test_je(self):
    self.assertEqual(
      parse_rasm("je target_name"),
      [Je("target_name")])
    self.assertEqual(
      parse_rasm("je lbl123"),
      [Je("lbl123")])

  def test_jne(self):
    self.assertEqual(
      parse_rasm("jne target_name"),
      [Jne("target_name")])
    self.assertEqual(
      parse_rasm("jne lbl123"),
      [Jne("lbl123")])

  def test_call(self):
    self.assertEqual(
      parse_rasm("call function_name"),
      [Call("function_name")])
    self.assertEqual(
      parse_rasm("call f01"),
      [Call("f01")])

  def test_ret(self):
    self.assertEqual(
      parse_rasm("ret"),
      [Ret()])

  def test_print(self):
    self.assertEqual(
      parse_rasm("print 10"),
      [Print(Imm(10))])
    self.assertEqual(
      parse_rasm("print [rsp + 40]"),
      [Print(StackOff(40))])

  def test_full_program(self):
    pgrm = """
    entry:
      mov 5.0, rans
      mov rans, [rsp + 2]
      add 0, rsp
      call function_fact_5150388492262006291
      sub 0, rsp
    """
    self.assertEqual(parse_rasm(pgrm), [
      Label("entry"),
      Mov(Imm(5), Rans()),
      Mov(Rans(), StackOff(2)),
      Add(Imm(0), Rsp()),
      Call("function_fact_5150388492262006291"),
      Sub(Imm(0), Rsp()),
    ])

  def test_empty(self):
    self.assertEqual(parse_rasm(""), [])

  def test_parse_errors(self):
    with self.assertRaises(ParseError):
      parse_rasm("jmp 16")
    with self.assertRaises(ParseError):
      parse_rasm("je add")
    with self.assertRaises(ParseError):
      parse_rasm("jne ]")
    with self.assertRaises(ParseError):
      parse_rasm("mov 2,")
    with self.assertRaises(ParseError):
      parse_rasm("add 3, [rsp + ]")
    with self.assertRaises(ParseError):
      parse_rasm("mov [rsp + 2.3], rans")
    with self.assertRaises(ParseError):
      parse_rasm("cmp ,")
    with self.assertRaises(ParseError):
      parse_rasm("not_an_instr")

  def test_lexer_errors(self):
    with self.assertRaises(LexError):
      parse_rasm("#@*&$*&#*$&")
    with self.assertRaises(LexError):
      parse_rasm("___")

if __name__ == '__main__':
  unittest.main()