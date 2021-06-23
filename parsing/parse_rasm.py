from typing import List
from enum import Enum, auto
from rasm.Instr import *
from rasm.Operand import *
from .Parser import *
from .Lexer import *

class RasmParser(Parser):
  
  def __init__(self, display_token_name):
    super().__init__(display_token_name)

  def parse(self, tokens: List[Token]) -> List[Instr]:
    """Parse a stream of tokens into a rasm program"""
    self.setup(tokens)

    instrs = []

    while not self.empty():
      if self.matches(Tok.LABEL):
        label = self.next().lexeme
        self.eat(Tok.COLON)
        instrs.append(Label(label))
      elif self.matches(Tok.MOV):
        self.parse_bin_op(Tok.MOV, Mov, instrs)
      elif self.matches(Tok.ADD):
        self.parse_bin_op(Tok.ADD, Add, instrs)
      elif self.matches(Tok.SUB):
        self.parse_bin_op(Tok.SUB, Sub, instrs)
      elif self.matches(Tok.MUL):
        self.parse_bin_op(Tok.MUL, Mul, instrs)
      elif self.matches(Tok.CMP):
        self.parse_bin_op(Tok.CMP, Cmp, instrs)
      elif self.matches(Tok.JMP):
        self.parse_jump(Tok.JMP, "jmp", Jmp, instrs)
      elif self.matches(Tok.JE):
        self.parse_jump(Tok.JE, "je", Je, instrs)
      elif self.matches(Tok.JNE):
        self.parse_jump(Tok.JNE, "jne", Jne, instrs)
      elif self.matches(Tok.CALL):
        self.parse_jump(Tok.CALL, "call", Call, instrs)
      elif self.matches(Tok.RET):
        self.eat(Tok.RET)
        instrs.append(Ret())
      elif self.matches(Tok.PRINT):
        self.eat(Tok.PRINT)
        op = self.parse_operand()
        instrs.append(Print(op))

    return instrs

  def parse_bin_op(self, tok_name, constructor, instrs: List[Instr]):
    """Parses a binary operator by parsing its name, source and dest operands,
    and adding a constructed ast node to the given list of instrs"""
    self.eat(tok_name)
    src = self.parse_operand()
    self.eat(Tok.COMMA)
    dest = self.parse_operand()
    instrs.append(constructor(src, dest))

  def parse_jump(self, jump_tok_name, jump_name: str, constructor, instrs: List[Instr]):
    """Parses a jump instruction (jmp, je, jne, call) by parsing its name
    then its target, ensuring the target is valid"""
    self.eat(jump_tok_name)
    target = self.next()
    if target.name != Tok.LABEL:
      raise ParseError(f"expected label target for {jump_name}, got {display_token_name(target.name)}")
    instrs.append(constructor(target.lexeme))

  def parse_operand(self) -> Operand:
    """Parse an operand off the token stream"""
    if self.empty():
      raise ParseError("unexpected end of rasm program: expected operand")

    if self.matches(Tok.NUM):
      immediate = self.next().lexeme
      return Imm(immediate)
    elif self.matches(Tok.RANS):
      self.eat(Tok.RANS)
      return Rans()
    elif self.matches(Tok.RSP):
      self.eat(Tok.RSP)
      return Rsp()
    elif self.matches(Tok.LBRACKET):
      self.eat(Tok.LBRACKET)
      self.eat(Tok.RSP)
      self.eat(Tok.PLUS)
      offset = self.next()
      if offset.name != Tok.NUM:
        raise ParseError(f"expected offset from rsp, got {display_token_name(offset.name)}")
      if not (offset.lexeme.is_integer() and offset.lexeme >= 0) :
        raise ParseError(f"expected positive integer stack offset, got {offset.lexeme}")
      self.eat(Tok.RBRACKET)
      # make sure offset is converted to int (it is safe to do so)
      return StackOff(int(offset.lexeme))
    else:
      raise ParseError(f"expected operand, got {display_token_name(self.peek().name)}")


class Tok(Enum):
  COMMA = auto()
  COLON = auto()
  LBRACKET = auto()
  RBRACKET = auto()
  PLUS = auto()
  NUM = auto()
  MOV = auto()
  ADD = auto()
  SUB = auto()
  MUL = auto()
  CMP = auto()
  LABEL = auto()
  JMP = auto()
  JE = auto()
  JNE = auto()
  CALL = auto()
  RET = auto()
  RANS = auto()
  RSP = auto()
  PRINT = auto()

def display_token_name(name: Tok) -> str:
  """Convert a token name into a user-facing string"""
  if name == Tok.COMMA:
    return "','"
  elif name == Tok.COLON:
    return "':'"
  elif name == Tok.LBRACKET:
    return "'['"
  elif name == Tok.RBRACKET:
    return "']'"
  elif name == Tok.PLUS:
    return "+"
  elif name == Tok.NUM:
    return "number"
  elif name == Tok.MOV:
    return "mov"
  elif name == Tok.ADD:
    return "add"
  elif name == Tok.SUB:
    return "sub"
  elif name == Tok.MUL:
    return "mul"
  elif name == Tok.CMP:
    return "cmp"
  elif name == Tok.LABEL:
    return "label"
  elif name == Tok.JMP:
    return "jmp"
  elif name == Tok.JE:
    return "je"
  elif name == Tok.JNE:
    return "jne"
  elif name == Tok.CALL:
    return "call"
  elif name == Tok.RET:
    return "ret"
  elif name == Tok.RANS:
    return "rans"
  elif name == Tok.RSP:
    return "rsp"
  elif name == Tok.PRINT:
    return "print"

# global lexer for rasm
lexer = Lexer([
  Pattern(r"\s+",                   lambda s: None),
  Pattern(r",",                     lambda s: Token(Tok.COMMA, None)),
  Pattern(r":",                     lambda s: Token(Tok.COLON, None)),
  Pattern(r"\[",                    lambda s: Token(Tok.LBRACKET, None)),
  Pattern(r"\]",                    lambda s: Token(Tok.RBRACKET, None)),
  Pattern(r"\+",                    lambda s: Token(Tok.PLUS, None)),
  Pattern(r"mov",                   lambda s: Token(Tok.MOV, None)),
  Pattern(r"add",                   lambda s: Token(Tok.ADD, None)),
  Pattern(r"sub",                   lambda s: Token(Tok.SUB, None)),
  Pattern(r"mul",                   lambda s: Token(Tok.MUL, None)),
  Pattern(r"cmp",                   lambda s: Token(Tok.CMP, None)),
  Pattern(r"jmp",                   lambda s: Token(Tok.JMP, None)),
  Pattern(r"je",                    lambda s: Token(Tok.JE, None)),
  Pattern(r"jne",                   lambda s: Token(Tok.JNE, None)),
  Pattern(r"call",                  lambda s: Token(Tok.CALL, None)),
  Pattern(r"ret",                   lambda s: Token(Tok.RET, None)),
  Pattern(r"rans",                  lambda s: Token(Tok.RANS, None)),
  Pattern(r"rsp",                   lambda s: Token(Tok.RSP, None)),
  Pattern(r"print",                 lambda s: Token(Tok.PRINT, None)),
  Pattern(r"[a-zA-Z][a-zA-Z0-9_]*", lambda s: Token(Tok.LABEL, s)),
  Pattern(r"-?[0-9]+(\.[0-9]+)?",   lambda s: Token(Tok.NUM, float(s))),
])

parser = RasmParser(display_token_name)

def parse_rasm(pgrm: str) -> List[Instr]:
  """Parses a rasm program into a list of instructions
  that can be executed by a VM"""
  tokens = lexer.lex(pgrm)
  return parser.parse(tokens)