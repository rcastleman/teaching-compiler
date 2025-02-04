from typing import List, TYPE_CHECKING
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
  index, and in a given environment. The generated program leaves 
  the expression's value in rans"""

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
    equal_end = gensym("equal_end")

    return compile_expr(exp.left,defns,si,env) + \
      [Mov(Rans(),StackOff(si))] + \
      compile_expr(exp.right, defns, si + 1, env) + \
        [Cmp(StackOff(si),Rans()), 
        Jne(not_equal), 
          Label(equal),
          Mov(Imm(1),Rans()),
          Jmp(equal_end),
        Label(not_equal),
          Mov(Imm(0),Rans()),
        Label(equal_end)]

  if exp.isIf():
    #   (code for cond here)
    # 	cmp rans, 0
    # 	je cond_is_zero
    # cond_is_NOT_zero:
    # 	(code for thn here)
    # 	jmp end
    # cond_is_zero:
    # 	(code for els here)
    # end:
    if_cond_zero = gensym("if_cond_false")
    if_cond_not_zero = gensym("if_cond_true")
    if_end = gensym("if_is_done")

    return compile_expr(exp.cond,defns,si,env) + \
        [Cmp(Rans(),Imm(0)),
          Je(if_cond_zero),
          Label(if_cond_not_zero)] + \
            compile_expr(exp.thn,defns,si,env) + \
            [Jmp(if_end),
          Label(if_cond_zero)] + \
            compile_expr(exp.els,defns,si,env) + \
          [Label(if_end)]


  if exp.isName():
    stack_index = env.lookup(exp.name)
    if stack_index is None:
      raise UnboundName(exp.name)	
    return [Mov(StackOff(stack_index),Rans())]

  if exp.isLet():
    # (code for value)
    # mov rans, [rsp + si]
    # (code for body)
    # don’t use si!!
    # name’s value is located at [rsp + si]
    incremented_si = si + 1
    modified_env = env.extend(exp.name,si)
  
    return compile_expr(exp.value,defns,si,env) + \
            [Mov(Rans(),StackOff(si))] + \
            compile_expr(exp.body,defns,incremented_si,modified_env)

  # App(fname: str, args: List[Expr])
  if exp.isApp():
    # (code for arg 0)
    # mov rans, [rsp + (si + 1)]
    # …
    # (code for arg n)
    # mov rans, [rsp + (si + 1 + n)]
    # 
    # add (si - 1), rsp
    # call function_label
    # sub (si -1), rsp
    
    deffin =lookup_defn(defns,exp.fname)
    
    if deffin is None:
      raise UndefinedFun(exp.fname)
    
    if len(deffin.params) != len(exp.args):
      raise ArityMismatch(exp.args,deffin)
  
    move_args_list = []
    i = 0

    for arg in exp.args:
      move_args_list += compile_expr(arg,defns,si+1+i,env) + \
        [Mov(Rans(),StackOff(si+1+i))]
      i+=1
    
    return move_args_list + [Add((Imm(si - 1)),Rsp())] + \
      [Call(function_label(exp.fname))] + [Sub((Imm(si - 1)),Rsp())]

  raise NotImplementedError("compile_expr")

def compile_defn(defn: Defn, defns: List[Defn]) -> List[Instr]:
  """Generates instructions for a function definition"""
  # Defn(name: str, params: List[str], body: Expr)
  # == Recipe ==
  # func:
  #   (code for body)
  #   ret

  # set up env
  new_env = Env()
  env_index = 1
  for parameter in defn.params:
    new_env = new_env.extend(parameter,env_index)
    env_index += 1
  
  si = len(defn.params) + 1

  return [Label(function_label(defn.name))] + \
        compile_expr(defn.body,defns,si,new_env) + \
          [Ret()]
