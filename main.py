from enum import Enum, auto
import random
import sys


MEM_SIZE = 4096
PGM_MEM_START = 0x200

NATIVE_WIDTH = 64
NATIVE_HEIGHT = 32
ASF = 10    # Arbitrary scale factor for pixels

BG_RED = 0x88
BG_GREEN = 0x88
BG_BLUE = 0x88


# Holds the names of all the operations
class Op(Enum):
    NONE = auto()   # unrecognized opcode
    NOP = auto()    # no operation
    SYS = auto()    # jump to routine (deprecated)
    CLS = auto()    # clear the display
    RET = auto()    # return from a subroutine
    JP = auto()     # jump to location (branch always)
    CALL = auto()   # call subroutine
    SE = auto()     # skip instruction if equal
    SNE = auto()    # skip instruction if not equal
    SER = auto()    # skip instruction if equal to register
    LD = auto()     # load
    ADD = auto()    # add direct
    LDR = auto()    # load register
    OR = auto()     # bitwise OR
    AND = auto()    # bitwise AND
    XOR = auto()    # bitwise XOR
    ADDR = auto()   # add register
    SUB = auto()    # subtract Vx - Vy
    SHR = auto()    # shift right
    SUBN = auto()   # subtract Vy - Vx
    SHL = auto()    # shift left
    SNER = auto()   # skip instruction if not equal to register
    LDI = auto()    # load I
    JPO = auto()    # jump to location plus offset
    RND = auto()    # random byte
    DRW = auto()    # display sprite
    SKP = auto()    # skip instruction if key pressed
    SKNP = auto()   # skip instruction if key not pressed
    LDDT = auto()   # load delay timer
    LDKP = auto()   # load key press (blocks)
    LDDTR = auto()  # load delay timer from register
    LDST = auto()   # load sound timer
    ADDI = auto()   # add Vx to I
    LDS = auto()    # load I with sprite location
    LDBCD = auto()  # store Vx in I, I+1, and I+2 in BCD format
    LDIR = auto()   # load registers V0-VF into memory starting at address I
    LDRI = auto()   # read starting at address I and store values in V0-VF


class Memory:

    def __init__(self, fill):
        self.mem = [fill for _ in range(MEM_SIZE)]

    def read8(self, addr):
        return self.mem[addr]

    # Read two bytes from the given address
    def read16(self, addr):
        # print(f"Memory::read16 first byte: {hex(self.mem[addr])}, second byte: {hex(self.mem[addr + 1])}")
        return (self.mem[addr] << 8) | self.mem[addr + 1]

    # Write one byte at the given address
    def write8(self, addr, data):
        self.mem[addr] = data

    def write16(self, addr, data):
        self.mem[addr] = (data >> 8) & 0xFF
        self.mem[addr + 1] = data & 0xFF


# Operations class that decodes opcodes and picks out relevant pieces
class Operator:

    @staticmethod
    def decode(opcode):
        op = Operator.op(opcode)
        n = Operator.n(opcode)
        kk = Operator.kk(opcode)
        operation = Op.NONE

        if opcode == 0x00E0: operation = Op.CLS
        elif opcode == 0x00EE: operation = Op.RET
        elif opcode == 0x0000: operation = Op.NONE
        # if op == 0x0000: operation = Op.SYS
        if op == 0x1000: operation = Op.JP
        elif op == 0x2000: operation = Op.CALL
        elif op == 0x3000: operation = Op.SE
        elif op == 0x4000: operation = Op.SNE
        elif op == 0x5000: operation = Op.SER
        elif op == 0x6000: operation = Op.LD
        elif op == 0x7000: operation = Op.ADD
        elif op == 0x8000:
            if n == 0x0: operation = Op.LD
            elif n == 0x1: operation = Op.OR
            elif n == 0x2: operation = Op.AND
            elif n == 0x3: operation = Op.XOR
            elif n == 0x4: operation = Op.ADDR
            elif n == 0x5: operation = Op.SUB
            elif n == 0x6: operation = Op.SHR
            elif n == 0x7: operation = Op.SUBN
            elif n == 0xE: operation = Op.SHL
        elif op == 0x9000: operation = Op.SNER
        elif op == 0xA000: operation = Op.LDI
        elif op == 0xB000: operation = Op.JPO
        elif op == 0xC000: operation = Op.RND
        elif op == 0xD000: operation = Op.DRW
        elif op == 0xE000:
            if kk == 0x9E: operation = Op.SKP
            elif kk == 0xA1: operation = Op.SKNP
        elif op == 0xF000:
            if kk == 0x07: operation = Op.LDDT
            elif kk == 0x0A: operation = Op.LDKP
            elif kk == 0x15: operation = Op.LDDTR
            elif kk == 0x18: operation = Op.LDST
            elif kk == 0x1E: operation = Op.ADDI
            elif kk == 0x29: operation = Op.LDS
            elif kk == 0x33: operation = Op.LDBCD
            elif kk == 0x55: operation = Op.LDIR
            elif kk == 0x65: operation = Op.LDRI

        if operation is Op.NONE: print(f"Invalid opcode: {format(opcode, '04X')}")

        return operation

    @staticmethod
    def op(opcode):
        return opcode & 0xF000

    @staticmethod
    def nnn(opcode):
        return opcode & 0x0FFF

    @staticmethod
    def x(opcode):
        return (opcode & 0x0F00) >> 8

    @staticmethod
    def y(opcode):
        return (opcode & 0x00F0) >> 4

    @staticmethod
    def kk(opcode):
        return opcode & 0x00FF

    @staticmethod
    def n(opcode):
        return opcode & 0xF


class CPU:

    BYTE_MAX_VALUE = 255    # Max value that can be stored in a byte (2**8)
    O = 0xF                 # CPU overflow register
    NUM_VREGS = 16          # The number of V registers

    def __init__(self, stack_size, debug=True):
        self.v = [0 for _ in range(CPU.NUM_VREGS)]  # the V registers
        self.i = 0   # The I register
        self.st = 0  # The sound timer register
        self.dt = 0  # The delay timer register
        self.pc = PGM_MEM_START  # The program counter
        self.sp = 0  # The stack pointer
        self.op = Op.NONE

        self.stack = [0 for _ in range(stack_size)]

        # For debugging
        self.debug = debug

    def cycle(self, memory):

        opcode = memory.read16(self.pc)

        self.op = Operator.decode(opcode)
        next_pc = self.pc + 2

        nnn = Operator.nnn(opcode)
        x = Operator.x(opcode)
        y = Operator.y(opcode)
        kk = Operator.kk(opcode)
        n = Operator.n(opcode)

        # format the trace strings ahead of time
        nnn_t = format(nnn, '#03X')
        x_t = f"V{format(x, '1X')}"
        y_t = f"V{format(y, '1X')}"
        kk_t = format(kk, '#02X')
        n_t = format(n, '#1X')
        xy_t = f"{x_t} {y_t}"
        xkk_t = f"{x_t} {kk_t}"

        trace_args = ""

        # Perform actions based upon
        if self.op == Op.SYS or self.op == Op.JP:
            next_pc = nnn
            trace_args = nnn_t

        elif self.op == Op.CLS:
            # TODO: clear screen
            pass

        elif self.op == Op.RET:
            # return from subroutine
            next_pc = self.stack[self.sp]
            self.sp -= 1

        elif self.op == Op.CALL:
            # call subroutine
            next_pc = nnn
            self.stack[self.sp] = self.pc
            self.sp += 1
            trace_args = nnn_t

        elif self.op == Op.SE:
            # skip inst if equal
            next_pc = self.pc + 4 if self.v[x] == kk else self.pc + 2
            trace_args = xkk_t

        elif self.op == Op.SNE:
            # skip inst if not equal
            next_pc = self.pc + 4 if self.v[x] != kk else self.pc + 2
            trace_args = xkk_t

        elif self.op == Op.SER:
            # skip inst if equal to register
            next_pc = self.pc + 4 if self.v[x] == self.v[y] else self.pc + 2
            trace_args = xy_t

        elif self.op == Op.LD:
            # load
            self.v[x] = kk
            trace_args = xkk_t

        elif self.op == Op.ADD:
            # add direct
            self.v[x] += kk
            trace_args = xkk_t

        elif self.op == Op.LDR:
            # load register
            self.v[x] = self.v[y]
            trace_args = xy_t

        elif self.op == Op.OR:
            # bitwise OR
            self.v[x] = self.v[x] | self.v[y]
            trace_args = xy_t

        elif self.op == Op.AND:
            # bitwise AND
            self.v[x] = self.v[x] & self.v[y]
            trace_args = xy_t

        elif self.op == Op.XOR:
            # bitwise XOR
            self.v[x] = self.v[x] ^ self.v[y]
            trace_args = xy_t

        elif self.op == Op.ADDR:
            # add register
            self.v[x] = self.v[x] + self.v[y]
            self.v[CPU.O] = 0 if self.v[x] <= CPU.BYTE_MAX_VALUE else 1
            self.v[x] &= 0xFF
            trace_args = xy_t

        elif self.op == Op.SUB:
            # subtract Vx - Vy
            self.v[x] = self.v[x] - self.v[y]
            self.v[CPU.O] = 1 if self.v[x] > self.v[y] else 0
            trace_args = xy_t

        elif self.op == Op.SHR:
            # shift right
            self.v[CPU.O] = self.v[x] & 0x1
            self.v[x] = self.v[x] >> 1
            trace_args = x_t

        elif self.op == Op.SUBN:
            # subtract Vy - Vx
            self.v[x] = self.v[y] - self.v[x]
            self.v[CPU.O] = 1 if self.v[y] > self.v[x] else 0
            trace_args = xy_t

        elif self.op == Op.SHL:
            # shift left
            self.v[CPU.O] = (self.v[x] & 0x80) >> 7
            self.v[x] = (self.v[x] << 1) * 0xFF
            trace_args = x_t

        elif self.op == Op.SNER:
            # skip inst if not equal to register
            next_pc = self.pc + 4 if self.v[x] != self.v[y] else self.pc + 2
            trace_args = xy_t

        elif self.op == Op.LDI:
            # load I
            self.i = nnn
            trace_args = nnn_t

        elif self.op == Op.JPO:
            # jump to location + offset
            self.pc = nnn + self.v[0]
            trace_args = nnn_t

        elif self.op == Op.RND:
            # random byte
            self.v[x] = random.randrange(0, CPU.BYTE_MAX_VALUE + 1, 1) & kk
            trace_args = xkk_t

        elif self.op == Op.DRW: pass # TODO: draw sprite
        elif self.op == Op.SKP: pass # TODO: skip inst if key pressed
        elif self.op == Op.SKNP: pass # TODO: skip inst if key not pressed
        elif self.op == Op.LDDT:
            # load delay timer into register
            self.v[x] = self.dt
            trace_args = x_t

        elif self.op == Op.LDKP:
            # TODO: load key press (blocking)
            pass

        elif self.op == Op.LDDTR:
            # load delay timer from register
            self.dt = self.v[x]
            trace_args = x_t

        elif self.op == Op.LDST:
            # load sound timer
            self.st = self.v[x]
            trace_args = x_t

        elif self.op == Op.ADDI:
            # add Vx to I
            self.i += self.v[x]
            trace_args = x_t

        elif self.op == Op.LDS:
            # TODO: load I with sprite location
            pass

        elif self.op == Op.LDBCD:
            # store Vx in I, I+1, and I+2 in BCD format
            h, t, o = self.bcd(self.v[x])
            memory.write8(self.i, h)
            memory.write8(self.i + 1, t)
            memory.write8(self.i + 2, o)
            trace_args = f"{h} {t} {o}"

        elif self.op == Op.LDIR:
            # load registers V0-Vx into memory starting at address I
            for i in range(x+1):
                memory.write8(self.i + i, self.v[i])

        elif self.op == Op.LDRI:
            # read starting at address I and store values in V0-Vx
            for i in range(x+1):
                self.v[i] = memory.read8(self.i + i)

        if self.op == Op.NONE:
            print(f"CHIP-8 encountered an error @ {format(self.pc, '03X')}")
            self.trace(opcode)
            return False # If the opcode we received was invalid, stop execution

        if self.debug:
            self.trace(opcode, trace_args)

        self.pc = next_pc
        return True

    # turns value into a 3-byte BCD representation
    def bcd(self, value):
        hundreds = value // 100
        tens = (value - (hundreds * 100)) // 10
        ones = value % 10
        return hundreds, tens, ones

    # Display a trace line of the current program counter, the opcode, the name of the opcode, and a opcode specific
    # arg string
    def trace(self, opcode, args=""):
        print(f"{format(self.pc, '#03X')}: {format(opcode, '#04X')} {self.op}{' ' * (8 - len(str(self.op)))} {args}")


class CHIP8:

    def __init__(self, debug_mode=True):
        self.mem = Memory(0)
        self.debug_mode = debug_mode
        self.stack_size = 16
        # self.display = Display(NATIVE_WIDTH, NATIVE_HEIGHT, ASF)

    def load_rom(self, path):
        with open(path, "rb") as rom_file:
            # Read the ROM from the filesystem
            rom_data = rom_file.read()
            # Load the rom data into ram

        for i in range(len(rom_data)):
            self.mem.write8(PGM_MEM_START + i, rom_data[i])

    def play(self):
        print("<addr>: <opcode> <op> <args...>")
        cpu = CPU(self.stack_size, debug=self.debug_mode)
        go = True
        while go:
            go = cpu.cycle(self.mem)


def main(args):
    print("*** CHIP-8 EMULATOR ***")

    chip8 = CHIP8(debug_mode=True)
    chip8.load_rom(args[0])
    chip8.play()

    print("THANK YOU FOR USING CHIP-8")


if __name__ == "__main__":
    # First argument should be the path to the ROM to be played
    main(sys.argv[1:])