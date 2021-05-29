from typing import List
from .Defn import *
from .Expr import *
from .Env import *
from .Errors import *
from .util import *
from rasm.Instr import *
from rasm.Operand import *

def compile(defns: List[Defn], body: Expr) -> List[Instr]:
  """Consumes a program (list of function definitions and a body) 
  and generates equivalent code in the target language"""
  # compile definitions
  defn_instrs = []
  for d in defns:
    defn_instrs += compile_defn(d, defns)

  # compile body
  body_instrs = compile_expr(body, defns, 1, Env())

  # emit definitions, then entry point
  return defn_instrs + [Label("entry")] + body_instrs

def compile_expr(exp: Expr, defns: List[Defn], si: int, env: Env) -> List[Instr]:
  """Generates instructions for a given expression, at a given stack
  index, and in a given environment"""

  if exp.isNum():
    return [Mov(Imm(exp.value), Rans())]

  if exp.isAdd1():
    return compile_expr(exp.operand,defns,si,env) + [Add(Imm(1),Rans())]
  
  if exp.isSub1():
    return compile_expr(exp.operand,defns,si,env) + [Sub(Imm(1),Rans())]

  raise NotImplementedError("compile_expr")

def compile_defn(defn: Defn, defns: List[Defn]) -> List[Instr]:
  """Generates instructions for a function definition"""
  raise NotImplementedError("compile_defn")