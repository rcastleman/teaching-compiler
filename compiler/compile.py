from typing import List
from .Defn import *
from .Expr import *
from .Env import *
from .Errors import *
from .util import *
from rasm.Instr import *
from rasm.Operand import *

def compile(defns: List[Defn], exprs: List[Expr]) -> List[Instr]:
  """Consumes a program (lists of function definitions and expressions) 
  and generates equivalent code in the target language"""
  # compile definitions
  defn_instrs = []
  for d in defns:
    defn_instrs += compile_defn(d, defns)

  # compile expressions
  expr_instrs = []
  for e in exprs:
    expr_instrs += compile_expr(e, defns, 1, Env())

  return defn_instrs + [Label("entry")] + expr_instrs

def compile_expr(exp: Expr, defns: List[Defn], si: int, env: Env) -> List[Instr]:
  """Generates instructions for a given expression, at a given stack
  index, and in a given environment. Leaves the expression's value in rans"""

  if exp.isNum():
    return [Mov(Imm(exp.value), Rans())]

  if exp.isAdd1():
    return compile_expr(exp.operand,defns,si,env) + [Add(Imm(1),Rans())]

  if exp.isSub1():
    return compile_expr(exp.operand,defns,si,env) + [Sub(Imm(1),Rans())]

  if exp.isPrintExpr(): # (print (+ 1 2))
    return compile_expr(exp.operand,defns,si,env) + [Print(Rans())]

  if exp.isPlus():
    # Compile left expression (into rans)
    # Store temporarily on stack
    # Compile right expression (into rans)
    # Add together (add instruction)
    return compile_expr(exp.left,defns,si,env) + \
    [Mov(Rans(),StackOff(si))] + \
    compile_expr(exp.right, defns, si + 1, env) + \
    [Add(StackOff(si), Rans())]

  if exp.isTimes():
    # Compile left expression (into rans)
    # Store temporarily on stack
    # Compile right expression (into rans)
    # Multiply together (mul instruction)
    return compile_expr(exp.left,defns,si,env) + \
    [Mov(Rans(),StackOff(si))] + \
    compile_expr(exp.right, defns, si + 1, env) + \
    [Mul(StackOff(si), Rans())]

  if exp.isMinus():
  # Compile left expression (into rans)
  # Store temporarily on stack
  # Compile right expression (into rans)
  # Subtract right from left (sub instruction)
    return compile_expr(exp.left,defns,si,env) + \
    [Mov(Rans(),StackOff(si))] + \
    compile_expr(exp.right, defns, si + 1, env) + \
    [Sub(Rans(),StackOff(si))] + \
    [Mov(StackOff(si),Rans())]

  if exp.isEquals():
    # cmp left, right
    # jne not_equal
    # equal:
    #   mov 1, rans
    #   jmp end
    # not_equal:
    #   mov 0, rans
    # end:
    equal = gensym("equal")
    not_equal = gensym("not_equal")
    end = gensym("end")

    return compile_expr(exp.left,defns,si,env) + \
      [Mov(Rans(),StackOff(si))] + \
      compile_expr(exp.right, defns, si + 1, env) + \
        [Cmp(StackOff(si),Rans()), 
        Jne(not_equal), 
          Label(equal),
          Mov(Imm(1),Rans()),
          Jmp(end),
        Label(not_equal),
          Mov(Imm(0),Rans()),
        Label(end)]

  raise NotImplementedError("compile_expr")

def compile_defn(defn: Defn, defns: List[Defn]) -> List[Instr]:
  """Generates instructions for a function definition"""
  raise NotImplementedError("compile_defn")