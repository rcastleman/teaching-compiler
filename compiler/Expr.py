
class Expr:
  """An Expr represents an expression in our language that can be 
  evaluated to produce a value (a number)"""

  def isNum(self):
    return isinstance(self, Num)

  def isAdd1(self):
    return isinstance(self, Add1)

  def isSub1(self):
    return isinstance(self, Sub1)

  def isPlus(self):
    return isinstance(self, Plus)

  def isMinus(self):
    return isinstance(self, Minus)

  def isTimes(self):
    return isinstance(self, Times)

  def isEquals(self):
    return isinstance(self, Equals)

  def isIf(self):
    return isinstance(self, If)

  def isLet(self):
    return isinstance(self, Let)

  def isApp(self):
    return isinstance(self, App)

  def isName(self):
    return isinstance(self, Name)

  def isPrintExpr(self):
    return isinstance(self, PrintExpr)

class Num(Expr):
  def __init__(self, value):
    self.value = value

  def __eq__(self, other):
    return isinstance(other, Num) and \
      self.value == other.value

  def __str__(self):
    if self.value.is_integer():
      return str(int(self.value))
    else:
      return str(self.value)

class Add1(Expr):
  def __init__(self, operand):
    self.operand = operand

  def __eq__(self, other):
    return isinstance(other, Add1) and \
      self.operand == other.operand

  def __str__(self):
    return f"(add1 {self.operand})"

class Sub1(Expr):
  def __init__(self, operand):
    self.operand = operand

  def __eq__(self, other):
    return isinstance(other, Sub1) and \
      self.operand == other.operand

  def __str__(self):
    return f"(sub1 {self.operand})"

class Plus(Expr):
  def __init__(self, left, right):
    self.left = left
    self.right = right

  def __eq__(self, other):
    return isinstance(other, Plus) and \
      self.left == other.left and \
      self.right == other.right

  def __str__(self):
    return f"(+ {self.left} {self.right})"

class Minus(Expr):
  def __init__(self, left, right):
    self.left = left
    self.right = right

  def __eq__(self, other):
    return isinstance(other, Minus) and \
      self.left == other.left and \
      self.right == other.right

  def __str__(self):
    return f"(- {self.left} {self.right})"

class Times(Expr):
  def __init__(self, left, right):
    self.left = left
    self.right = right

  def __eq__(self, other):
    return isinstance(other, Times) and \
      self.left == other.left and \
      self.right == other.right

  def __str__(self):
    return f"(* {self.left} {self.right})"

class Equals(Expr):
  def __init__(self, left, right):
    self.left = left
    self.right = right

  def __eq__(self, other):
    return isinstance(other, Equals) and \
      self.left == other.left and \
      self.right == other.right

  def __str__(self):
    return f"(= {self.left} {self.right})"

class If(Expr):
  def __init__(self, cond, thn, els):
    self.cond = cond
    self.thn = thn
    self.els = els

  def __eq__(self, other):
    return isinstance(other, If) and \
      self.cond == other.cond and \
      self.thn == other.thn and \
      self.els == other.els

  def __str__(self):
    return f"(if {self.cond} {self.thn} {self.els})"

class Let(Expr):
  def __init__(self, name, value, body):
    self.name = name
    self.value = value
    self.body = body

  def __eq__(self, other):
    return isinstance(other, Let) and \
      self.name == other.name and \
      self.value == other.value and \
      self.body == other.body

  def __str__(self):
    return f"(let ({self.name} {self.value}) {self.body})"

class App(Expr):
  def __init__(self, fname, args):
    self.fname = fname
    self.args = args

  def __eq__(self, other):
    return isinstance(other, App) and \
      self.fname == other.fname and \
      self.args == other.args 

  def __str__(self):
    args = " ".join(map(lambda a: str(a), self.args))
    return f"({self.fname} {args})"

class Name(Expr):
  def __init__(self, name):
    self.name = name

  def __eq__(self, other):
    return isinstance(other, Name) and \
      self.name == other.name 

  def __str__(self):
    return self.name

class PrintExpr(Expr):
  def __init__(self, operand):
    self.operand = operand

  def __eq__(self, other):
    return isinstance(other, PrintExpr) and \
      self.operand == other.operand

  def __str__(self):
    return f"(print {self.operand})"
