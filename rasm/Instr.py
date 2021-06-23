
class Instr:
  def isMov(self):
    return isinstance(self, Mov)

  def isAdd(self):
    return isinstance(self, Add)

  def isSub(self):
    return isinstance(self, Sub)

  def isMul(self):
    return isinstance(self, Mul)

  def isCmp(self):
    return isinstance(self, Cmp)

  def isLabel(self):
    return isinstance(self, Label)

  def isJmp(self):
    return isinstance(self, Jmp)

  def isJe(self):
    return isinstance(self, Je)

  def isJne(self):
    return isinstance(self, Jne)

  def isCall(self):
    return isinstance(self, Call)

  def isRet(self):
    return isinstance(self, Ret)

  def isPrint(self):
    return isinstance(self, Print)

class Mov(Instr):
  def __init__(self, src, dest):
    self.src = src
    self.dest = dest

  def __eq__(self, other):
    return isinstance(other, Mov) and \
      self.src == other.src and \
      self.dest == other.dest

  def __str__(self):
    return f"\tmov {self.src}, {self.dest}"

class Add(Instr):
  def __init__(self, src, dest):
    self.src = src
    self.dest = dest

  def __eq__(self, other):
    return isinstance(other, Add) and \
      self.src == other.src and \
      self.dest == other.dest

  def __str__(self):
    return f"\tadd {self.src}, {self.dest}"

class Sub(Instr):
  def __init__(self, src, dest):
    self.src = src
    self.dest = dest

  def __eq__(self, other):
    return isinstance(other, Sub) and \
      self.src == other.src and \
      self.dest == other.dest

  def __str__(self):
    return f"\tsub {self.src}, {self.dest}"

class Mul(Instr):
  def __init__(self, src, dest):
    self.src = src
    self.dest = dest

  def __eq__(self, other):
    return isinstance(other, Mul) and \
      self.src == other.src and \
      self.dest == other.dest

  def __str__(self):
    return f"\tmul {self.src}, {self.dest}"

class Cmp(Instr):
  def __init__(self, left, right):
    self.left = left
    self.right = right

  def __eq__(self, other):
    return isinstance(other, Cmp) and \
      self.left == other.left and \
      self.right == other.right

  def __str__(self):
    return f"\tcmp {self.left}, {self.right}"

class Label(Instr):
  def __init__(self, label):
    self.label = label
  
  def __eq__(self, other):
    return isinstance(other, Label) and \
      self.label == other.label

  def __str__(self):
    return f"{self.label}:"
  
class Jmp(Instr):
  def __init__(self, target):
    self.target = target
  
  def __eq__(self, other):
    return isinstance(other, Jmp) and \
      self.target == other.target

  def __str__(self):
    return f"\tjmp {self.target}"

class Je(Instr):
  def __init__(self, target):
    self.target = target
  
  def __eq__(self, other):
    return isinstance(other, Je) and \
      self.target == other.target

  def __str__(self):
    return f"\tje {self.target}"

class Jne(Instr):
  def __init__(self, target):
    self.target = target
  
  def __eq__(self, other):
    return isinstance(other, Jne) and \
      self.target == other.target

  def __str__(self):
    return f"\tjne {self.target}"

class Call(Instr):
  def __init__(self, target):
    self.target = target

  def __eq__(self, other):
    return isinstance(other, Call) and \
      self.target == other.target

  def __str__(self):
    return f"\tcall {self.target}"

class Ret(Instr):
  def __init__(self):
    pass

  def __eq__(self, other):
    return isinstance(other, Ret)

  def __str__(self):
    return "\tret"

class Print(Instr):
  def __init__(self, operand):
    self.operand = operand

  def __eq__(self, other):
    return isinstance(other, Print) and \
      self.operand == other.operand

  def __str__(self):
    return f"\tprint {self.operand}"
