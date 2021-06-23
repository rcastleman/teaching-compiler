from typing import List
from compiler.Defn import *
from compiler.Expr import *
from compiler.Env import *
from compiler.Errors import *
from compiler.util import *
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
  index, and in a given environment"""
  if exp.isNum():
    # put the number in rans
    return [Mov(Imm(exp.value), Rans())]

  if exp.isAdd1():
    # compile operand into rans, then add 1 to it
    op_instrs = compile_expr(exp.operand, defns, si, env)
    return op_instrs + [Add(Imm(1), Rans())]

  elif exp.isSub1():
    # compile operand into rans, then sub 1 from it
    op_instrs = compile_expr(exp.operand, defns, si, env)
    return op_instrs + [Sub(Imm(1), Rans())]

  elif exp.isPrintExpr():
    # compile operand into rans, then print rans
    op_instrs = compile_expr(exp.operand, defns, si, env)
    return op_instrs + [Print(Rans())]

  elif exp.isPlus():
    # compile left, store on stack
    # compile right, then add stored left to rans
    left_instrs =   compile_expr(exp.left, defns, si, env)
    store_left =    [Mov(Rans(), StackOff(si))]
    right_instrs =  compile_expr(exp.right, defns, si + 1, env)
    perform_add =   [Add(StackOff(si), Rans())]
    return left_instrs + store_left + right_instrs + perform_add

  elif exp.isMinus():
    # compile left, store on stack
    # compile right, then subtract rans from it 
    # and move difference into rans
    left_instrs =   compile_expr(exp.left, defns, si, env)
    store_left =    [Mov(Rans(), StackOff(si))]
    right_instrs =  compile_expr(exp.right, defns, si + 1, env)
    sub_and_mov =   [Sub(Rans(), StackOff(si)), Mov(StackOff(si), Rans())]
    return left_instrs + store_left + right_instrs + sub_and_mov

  elif exp.isTimes():
    # compile left, store on stack
    # compile right, then perform multiply
    left_instrs =   compile_expr(exp.left, defns, si, env)
    store_left =    [Mov(Rans(), StackOff(si))]
    right_instrs =  compile_expr(exp.right, defns, si + 1, env)
    perform_mul =   [Mul(StackOff(si), Rans())]
    return left_instrs + store_left + right_instrs + perform_mul

  elif exp.isEquals():
    not_equal_lbl = gensym("not_equal")
    continue_lbl = gensym("continue")

    # compile left, store on stack
    # compile right
    # compare left/right:
    #   if == put 1 in rans
    #   if != put 0 in rans
    left_instrs =   compile_expr(exp.left, defns, si, env)
    store_left =    [Mov(Rans(), StackOff(si))]
    right_instrs =  compile_expr(exp.right, defns, si + 1, env)
    cmp_and_make_bool = [
      Cmp(StackOff(si), Rans()),
      Jne(not_equal_lbl),
      Mov(Imm(1), Rans()),
      Jmp(continue_lbl),
      Label(not_equal_lbl),
      Mov(Imm(0), Rans()),
      Label(continue_lbl)
    ]

    return left_instrs + store_left + right_instrs + cmp_and_make_bool

  elif exp.isIf():
    else_lbl = gensym("else")
    continue_lbl = gensym("continue")

    # compile condition
    # cmp with 0, if 0 then jmp to else code
    # compile then branch
    # after then, jmp to end
    cond_instrs =       compile_expr(exp.cond, defns, si, env)
    jmp_else_if_false = [Cmp(Imm(0), Rans()), Je(else_lbl)]
    thn_instrs =        compile_expr(exp.thn, defns, si, env)
    end_thn_start_els = [Jmp(continue_lbl), Label(else_lbl)]
    els_instrs =        compile_expr(exp.els, defns, si, env)
    end =               [Label(continue_lbl)]

    return cond_instrs + jmp_else_if_false + thn_instrs + \
      end_thn_start_els + els_instrs + end

  elif exp.isLet():
    # compile value, store on stack
    value_instrs = compile_expr(exp.value, defns, si, env)
    store_value = [Mov(Rans(), StackOff(si))]

    # compile body in env with name bound to stack index of value
    ext_env = env.extend(exp.name, si)
    body_instrs = compile_expr(exp.body, defns, si + 1, ext_env)

    return value_instrs + store_value + body_instrs

  elif exp.isApp():
    # look up function being applied
    defn = lookup_defn(defns, exp.fname)

    if defn is None:
      raise UndefinedFun(exp.fname)

    # check number of actual args against number of params
    if len(exp.args) != len(defn.params):
      raise ArityMismatch(exp.args, defn)

    # stack base is highest currently in-use stack index
    stack_base_idx = si - 1
    function_lbl = function_label(defn.name)

    arg_instrs = []
    for i in range(len(exp.args)):
      arg = exp.args[i]

      # arguments start at stack base + 2
      # return addr goes at stack base + 1
      arg_si = stack_base_idx + 2 + i

      # compile argument, move onto stack
      arg_instrs += compile_expr(arg, defns, arg_si, env)
      arg_instrs += [Mov(Rans(), StackOff(arg_si))]

    # make rsp point to stack base for duration 
    # of call, then restore afterwards
    call_instrs = [
      Add(Imm(stack_base_idx), Rsp()),
      Call(function_lbl),
      Sub(Imm(stack_base_idx), Rsp())
    ]

    return arg_instrs + call_instrs

  elif exp.isName():
    # look up name in environment
    name_si = env.lookup(exp.name)

    if name_si is None:
      raise UnboundName(exp.name)

    # put whatever's on the stack at indicated loc into rans
    return [Mov(StackOff(name_si), Rans())]

  else:
    raise ValueError(f"compile_expr: unexpected expression: {exp}")

def compile_defn(defn: Defn, defns: List[Defn]) -> List[Instr]:
  """Generates instructions for a function definition"""
  # bind parameters to successive stack locs starting at si = 1
  # si = 0 is the return address
  env = Env()
  for i in range(len(defn.params)):
    param = defn.params[i]
    env = env.extend(param, i + 1)

  # next si is stack index after all arguments (and ret addr)
  next_si = len(defn.params) + 1

  # function label, then body, then return
  label_instr = [Label(function_label(defn.name))]
  body_instrs = compile_expr(defn.body, defns, next_si, env)
  ret =         [Ret()]

  return label_instr + body_instrs + ret