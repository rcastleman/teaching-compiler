from typing import List, Tuple
from enum import Enum, auto
from compiler.Defn import *
from compiler.Expr import *
from .Lexer import *
from .Parser import *

class ProgramParser(Parser):

  def __init__(self, display_token_name):
    super().__init__(display_token_name)

  def parse(self, tokens: List[Token]) -> Tuple[List[Defn], List[Expr]]:
    """Parses a full program (defns and then a body) from its 
    input token stream"""
    # initialize parser state
    self.setup(tokens)

    # parse any defns in the program
    defns = []
    defn_prefix = [Tok.LPAREN, Tok.DEF]
    while self.matches_prefix(defn_prefix):
      defns.append(self.parse_defn())

    # parse expressions for the rest of the program
    exprs = []
    while self.index < len(self.tokens):
      exprs.append(self.parse_expr())

    # check defns for uniqueness
    defn_names = set()
    for d in defns:
      if d.name in defn_names:
        raise ParseError(f"function {d.name} defined more than once")
      else:
        defn_names.add(d.name)

    return (defns, exprs)

  def parse_defn(self) -> Defn:
    if self.empty():
      raise ParseError("unexpected end of program: expected a defn")

    self.eat_prefix([
      Tok.LPAREN,
      Tok.DEF,
      Tok.LPAREN,
    ])

    # function name should be a valid symbol
    if not self.matches(Tok.SYM):
      raise ParseError(
        f"invalid function name: {display_token_name(self.peek().name)}")
    fname = self.next().lexeme

    # parse parameter names (symbols)
    params = []
    while self.matches(Tok.SYM):
      params.append(self.next().lexeme)

    # closing paren for param list
    self.eat(Tok.RPAREN)

    # parse body and defn closing paren
    body = self.parse_expr()
    self.eat(Tok.RPAREN)

    return Defn(fname, params, body)

  def parse_expr(self) -> Expr:
    """Parses an expression off the input stream"""
    if self.empty():
      raise ParseError("unexpected end of program: expected expression")

    if self.matches(Tok.LPAREN):
      self.eat(Tok.LPAREN)

      if self.matches(Tok.ADD1):
        self.eat(Tok.ADD1)
        operand = self.parse_expr()
        self.eat(Tok.RPAREN)
        return Add1(operand)

      elif self.matches(Tok.SUB1):
        self.eat(Tok.SUB1)
        operand = self.parse_expr()
        self.eat(Tok.RPAREN)
        return Sub1(operand)

      elif self.matches(Tok.PLUS):
        self.eat(Tok.PLUS)
        left = self.parse_expr()
        right = self.parse_expr()
        self.eat(Tok.RPAREN)
        return Plus(left, right)

      elif self.matches(Tok.MINUS):
        self.eat(Tok.MINUS)
        left = self.parse_expr()
        right = self.parse_expr()
        self.eat(Tok.RPAREN)
        return Minus(left, right)

      elif self.matches(Tok.TIMES):
        self.eat(Tok.TIMES)
        left = self.parse_expr()
        right = self.parse_expr()
        self.eat(Tok.RPAREN)
        return Times(left, right)

      elif self.matches(Tok.EQUALS):
        self.eat(Tok.EQUALS)
        left = self.parse_expr()
        right = self.parse_expr()
        self.eat(Tok.RPAREN)
        return Equals(left, right)

      elif self.matches(Tok.PRINTEXPR):
        self.eat(Tok.PRINTEXPR)
        operand = self.parse_expr()
        self.eat(Tok.RPAREN)

        return PrintExpr(operand)

      # conditionals
      elif self.matches(Tok.IF):
        self.eat(Tok.IF)
        cond = self.parse_expr()
        thn = self.parse_expr()
        els = self.parse_expr()
        self.eat(Tok.RPAREN)
        return If(cond, thn, els)

      # let bindings
      elif self.matches(Tok.LET):
        self.eat(Tok.LET)
        self.eat(Tok.LPAREN)

        if not self.matches(Tok.SYM):
          raise ParseError(
            f"invalid identifier name: {display_token_name(self.peek().name)}")
        
        name = self.next().lexeme
        value = self.parse_expr()
        self.eat(Tok.RPAREN)
        body = self.parse_expr()
        self.eat(Tok.RPAREN)

        return Let(name, value, body)

      # must be an App
      else:
        if not self.matches(Tok.SYM):
          raise ParseError(
            f"invalid function in application: {display_token_name(self.peek().name)}")

        name = self.next().lexeme
        args = []
        while not self.matches(Tok.RPAREN):
          args.append(self.parse_expr())
        
        self.eat(Tok.RPAREN)
        return App(name, args)

    # number literals
    elif self.matches(Tok.NUM):
      n = self.next().lexeme
      return Num(n)

    # identifier names
    elif self.matches(Tok.SYM):
      name = self.next().lexeme
      return Name(name)

    else:
      raise ParseError(
        f"invalid expression near {display_token_name(self.peek().name)}")

class Tok(Enum):
  LPAREN = auto()
  RPAREN = auto()
  SYM = auto()
  NUM = auto()
  DEF = auto()
  ADD1 = auto()
  SUB1 = auto()
  PLUS = auto()
  MINUS = auto()
  TIMES = auto()
  EQUALS = auto()
  IF = auto()
  LET = auto()
  PRINTEXPR = auto()

def display_token_name(name: Tok) -> str:
  """Convert a token name into a user-facing string"""
  if name == Tok.LPAREN:
    return "'('"
  elif name == Tok.RPAREN:
    return "')'"
  elif name == Tok.SYM:
    return "symbol"
  elif name == Tok.NUM:
    return "number"
  elif name == Tok.DEF:
    return "def"
  elif name == Tok.ADD1:
    return "add1"
  elif name == Tok.SUB1:
    return "sub1"
  elif name == Tok.PLUS:
    return "+"
  elif name == Tok.MINUS:
    return "-"
  elif name == Tok.TIMES:
    return "*"
  elif name == Tok.EQUALS:
    return "="
  elif name == Tok.IF:
    return "'if'"
  elif name == Tok.LET:
    return "'let'"
  elif name == Tok.PRINTEXPR:
    return "print"

# global lexer for programs
lexer = Lexer([
  Pattern(r"\(",                        lambda s: Token(Tok.LPAREN, None)),
  Pattern(r"\)",                        lambda s: Token(Tok.RPAREN, None)),
  Pattern(r"\s+",                       lambda s: None),
  Pattern(r";.*?(\n|$)",                lambda s: None),
  Pattern(r"def",                       lambda s: Token(Tok.DEF, None)),
  Pattern(r"add1",                      lambda s: Token(Tok.ADD1, None)),
  Pattern(r"sub1",                      lambda s: Token(Tok.SUB1, None)),
  Pattern(r"\+",                        lambda s: Token(Tok.PLUS, None)),
  Pattern(r"\-",                        lambda s: Token(Tok.MINUS, None)),
  Pattern(r"\*",                        lambda s: Token(Tok.TIMES, None)),
  Pattern(r"=",                         lambda s: Token(Tok.EQUALS, None)),
  Pattern(r"if",                        lambda s: Token(Tok.IF, None)),
  Pattern(r"let",                       lambda s: Token(Tok.LET, None)),
  Pattern(r"print",                     lambda s: Token(Tok.PRINTEXPR, None)),
  Pattern(r"-?[0-9]+(\.[0-9]+)?",       lambda s: Token(Tok.NUM, float(s))),
  Pattern(r"[a-zA-Z][a-zA-Z0-9\?\!-]*", lambda s: Token(Tok.SYM, s)),
])

# global parser for programs
parser = ProgramParser(display_token_name)

def parse_program(pgrm: str) -> Tuple[List[Defn], List[Expr]]:
  """Parses a string program to produce a list of function
  definitions and a program body expression"""
  tokens = lexer.lex(pgrm)
  return parser.parse(tokens)