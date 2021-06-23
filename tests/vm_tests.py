import unittest
from rasm.VirtualMachine import *

ENTRY_LABEL = "entry"

def from_program(pgrm: list) -> VirtualMachine:
  """Creates a virtual machine and runs it on the 
  given program, for testing purposes"""
  vm = VirtualMachine()
  vm.execute(pgrm, suppress_output=True)
  return vm

# tests for the rasm virtual machine
class VMTests(unittest.TestCase):

  def assert_rans(self, rans: int, pgrm: list):
    """Run the given program in a VM and assert
    that the computed rans matches the given rans"""
    vm = VirtualMachine()
    vm.execute(pgrm, suppress_output=True)
    self.assertEqual(vm.rans, rans)

  def test_simple(self):
    vm = VirtualMachine()
    vm.execute([
      Label(ENTRY_LABEL),
      Mov(Imm(5), Rans())
    ], suppress_output=True)

    self.assertEqual(vm.rans, 5)
    self.assertEqual(vm.rip, 2)
    self.assertEqual(vm.rsp, 0)
    self.assertEqual(vm.fequal, False)
    self.assertEqual(vm.fless, False)

  def test_mov(self):
    self.assert_rans(20, [
      Label(ENTRY_LABEL),
      Mov(Imm(5), Rans()),
      Mov(Rans(), Rsp()),
      Mov(Imm(20), Rsp()),
      Mov(Rsp(), Rans())
    ])
    self.assert_rans(10, [
      Label(ENTRY_LABEL),
      Mov(Imm(5), StackOff(1)),
      Mov(Imm(10), StackOff(2)),
      Mov(StackOff(2), StackOff(1)),
      Mov(StackOff(1), Rans())
    ])
    with self.assertRaises(BadDest):
      from_program([
        Label(ENTRY_LABEL),
        Mov(Imm(3), Imm(4))])
    with self.assertRaises(BadStackAccess):
      from_program([
        Label(ENTRY_LABEL),
        Mov(StackOff(-1), Rans())])
    with self.assertRaises(BadStackAccess):
      from_program([
        Label(ENTRY_LABEL),
        Mov(Rsp(), StackOff(STACK_SIZE + 1))])
    with self.assertRaises(InvalidRsp):
      from_program([
        Label("f"),
        Ret(),
        Label(ENTRY_LABEL),
        Mov(Imm(-17), Rsp()),
        Call("f")
      ])

  def test_add(self):
    self.assert_rans(35, [
      Label(ENTRY_LABEL),
      Mov(Imm(30), Rans()),
      Add(Imm(5), Rans())
    ])
    self.assert_rans(9, [
      Label(ENTRY_LABEL),
      Mov(Imm(2), Rsp()),
      Mov(Imm(7), Rans()),
      Add(Rsp(), Rans())
    ])
    self.assert_rans(-145, [
      Label(ENTRY_LABEL),
      Mov(Imm(-100), Rans()),
      Add(Imm(5), Rans()),
      Add(Imm(-50), Rans())
    ])

  def test_sub(self):
    self.assert_rans(15, [
      Label(ENTRY_LABEL),
      Mov(Imm(17), Rans()),
      Sub(Imm(2), Rans())
    ])
    self.assert_rans(70, [
      Label(ENTRY_LABEL),
      Mov(Imm(77), Rans()),
      Mov(Imm(7), StackOff(1)),
      Sub(StackOff(1), Rans())
    ])
  
  def test_mul(self):
    self.assert_rans(12, [
      Label(ENTRY_LABEL),
      Mov(Imm(3), Rans()),
      Mul(Imm(4), Rans())
    ])
    self.assert_rans(50, [
      Label(ENTRY_LABEL),
      Mov(Imm(10), StackOff(1)),
      Mov(Imm(5), StackOff(2)),
      Mul(StackOff(2), StackOff(1)),
      Mov(StackOff(1), Rans())
    ])

  def test_cmp(self):
    vm1 = from_program([
      Label(ENTRY_LABEL),
      Mov(Imm(11), Rans()),
      Mov(Imm(11), StackOff(1)),
      Cmp(Rans(), StackOff(1))
    ])
    self.assertEqual(vm1.rans, 11)
    self.assertEqual(vm1.fequal, True)
    self.assertEqual(vm1.fless, False)

    vm2 = from_program([
      Label(ENTRY_LABEL),
      Mov(Imm(40), Rans()),
      Mov(Imm(16), StackOff(1)),
      Cmp(StackOff(1), Rans())
    ])
    self.assertEqual(vm2.rans, 40)
    self.assertEqual(vm2.fequal, False)
    self.assertEqual(vm2.fless, True)

    vm3 = from_program([
      Label(ENTRY_LABEL),
      Mov(Imm(-5), Rans()),
      Mov(Imm(-3), Rsp()),
      Cmp(Rsp(), Rans())
    ])
    self.assertEqual(vm3.rans, -5)
    self.assertEqual(vm3.fequal, False)
    self.assertEqual(vm3.fless, False)

  def test_label(self):
    # labels do no harm
    self.assert_rans(20, [
      Label(ENTRY_LABEL),
      Mov(Imm(20), Rans()),
      Label("l1"),
      Label("l2"),
      Label("l3"),
    ])
    # execution begins at the entry
    self.assert_rans(0, [
      Mov(Imm(100), Rans()),
      Label(ENTRY_LABEL),
    ])
    with self.assertRaises(DuplicateLabel):
      from_program([
        Label(ENTRY_LABEL),
        Label("a"),
        Label("b"),
        Label("a")
      ])
    with self.assertRaises(NoEntry):
      from_program([
        Mov(Imm(2), Rans())
      ])

  def test_jmp(self):
    self.assert_rans(2, [
      Label(ENTRY_LABEL),
      Mov(Imm(2), Rans()),
      Jmp("continue"),
      Mov(Imm(4), Rans()),
      Label("continue")
    ])
    self.assert_rans(1, [
      Label(ENTRY_LABEL),
      Mov(Imm(1), Rans()),
      Label("top"),
      Jmp("end"),
      Mov(Imm(40), Rans()),
      Add(Imm(2), Rans()),
      Jmp("top"),
      Label("end")
    ])
    with self.assertRaises(InvalidTarget):
      from_program([
        Label(ENTRY_LABEL),
        Jmp("no_label")
      ])

  def test_je(self):
    self.assert_rans(1, [
      Label(ENTRY_LABEL),
      Mov(Imm(5), Rans()),
      Mov(Imm(2), StackOff(1)),
      Add(Imm(3), StackOff(1)),
      Cmp(StackOff(1), Rans()),
      Je("equal"),
      Mov(Imm(0), Rans()),
      Jmp("continue"),
      Label("equal"),
      Mov(Imm(1), Rans()),
      Label("continue")
    ])
    self.assert_rans(0, [
      Label(ENTRY_LABEL),
      Mov(Imm(4), Rans()),
      Mov(Imm(7), Rsp()),
      Cmp(Rsp(), Rans()),
      Je("equal"),
      Mov(Imm(0), Rans()),
      Jmp("continue"),
      Label("equal"),
      Mov(Imm(1), Rans()),
      Label("continue")
    ])

  def test_jne(self):
    self.assert_rans(0, [
      Label(ENTRY_LABEL),
      Mov(Imm(5), Rans()),
      Mov(Imm(2), StackOff(1)),
      Add(Imm(3), StackOff(1)),
      Cmp(StackOff(1), Rans()),
      Jne("not_equal"),
      Mov(Imm(0), Rans()),
      Jmp("continue"),
      Label("not_equal"),
      Mov(Imm(1), Rans()),
      Label("continue")
    ])
    self.assert_rans(1, [
      Label(ENTRY_LABEL),
      Mov(Imm(4), Rans()),
      Mov(Imm(7), Rsp()),
      Cmp(Rsp(), Rans()),
      Jne("not_equal"),
      Mov(Imm(0), Rans()),
      Jmp("continue"),
      Label("not_equal"),
      Mov(Imm(1), Rans()),
      Label("continue")
    ])

  def test_call_ret(self):
    vm1 = from_program([
      Label("no_args"),
      Mov(Imm(7), Rans()),
      Ret(),
      Label(ENTRY_LABEL),
      Call("no_args"),
    ])
    self.assertEqual(vm1.rans, 7)
    self.assertEqual(vm1.rsp, 0)

    vm2 = from_program([
      Label("one_arg"),
      Mov(StackOff(1), Rans()),
      Ret(),
      Label(ENTRY_LABEL),
      Mov(Imm(4), StackOff(2)),
      Call("one_arg"),
    ])
    self.assertEqual(vm2.rans, 4)
    self.assertEqual(vm2.rsp, 0)

    # test with let bindings so rsp must be adjusted before/after call
    vm3 = from_program([
      Label("fun"),
      Mov(StackOff(1), Rans()),
      Add(StackOff(2), Rans()),
      Ret(),
      Label(ENTRY_LABEL),
      # bindings
      Mov(Imm(3), StackOff(1)),
      Mov(Imm(4), StackOff(2)),
      Mov(Imm(5), StackOff(3)),
      # function args
      Mov(StackOff(2), StackOff(5)),
      Mov(StackOff(1), StackOff(6)),
      # call with adjusted rsp
      Add(Imm(3), Rsp()),
      Call("fun"),
      Sub(Imm(3), Rsp())
    ])
    self.assertEqual(vm3.rans, 7)
    self.assertEqual(vm3.rsp, 0)
    # inspect the stack to make sure nothing got corrupted by call
    self.assertEqual(vm3.stack[1], 3)
    self.assertEqual(vm3.stack[2], 4)
    self.assertEqual(vm3.stack[3], 5)
    self.assertEqual(vm3.stack[5], 4)
    self.assertEqual(vm3.stack[6], 3)

    with self.assertRaises(InvalidTarget):
      from_program([
        Label(ENTRY_LABEL),
        Call("no_target")
      ])

  def test_various_exns(self):
    with self.assertRaises(BadDest):
      from_program([
        Label(ENTRY_LABEL),
        Mov(Imm(5), Imm(0))
      ])
    with self.assertRaises(BadStackAccess):
      from_program([
        Label(ENTRY_LABEL),
        Add(StackOff(-1), Rans())
      ])
    with self.assertRaises(InvalidInstr):
      from_program([
        Label(ENTRY_LABEL),
        Instr() # not a real instruction
      ])
    with self.assertRaises(InvalidTarget):
      from_program([
        Label(ENTRY_LABEL),
        Jmp("non_existent")
      ])
    with self.assertRaises(BadStackAccess):
      from_program([
        Label(ENTRY_LABEL),
        Sub(Imm(1), Rsp()), # makes rsp -1
        Mov(StackOff(0), Rans())
      ])
    with self.assertRaises(DuplicateLabel):
      from_program([
        Label(ENTRY_LABEL),
        Label(ENTRY_LABEL)
      ])
    with self.assertRaises(NoEntry):
      from_program([
        Mov(Imm(1), Rans())
      ])
    # this will overflow the stack eventually with ret addrs
    with self.assertRaises(InvalidRsp):
      from_program([
        Label(ENTRY_LABEL),
        Call(ENTRY_LABEL)
      ])


if __name__ == '__main__':
  unittest.main()