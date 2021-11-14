#!/bin/python
from enum import Enum, auto
import sys

class Instr(Enum):
    S = auto()
    T = auto()
    L = auto()

tokens = {
    ' ':  Instr.S,
    '\t': Instr.T,
    '\n': Instr.L
}

symbols = { v: k for k, v in tokens.items() }

def tokenize(inp):
    return list(
           map(lambda c: tokens[c],
           filter(lambda c: c in tokens.keys(),
                  inp)))

class IMP(Enum):
    S  = auto()
    L  = auto()
    TS = auto()
    TT = auto()
    TL = auto()

def read_imp(inp, ip):
    imp = None

    c1 = inp[ip]
    ip += 1

    if c1 == Instr.S:
        imp = IMP.S

    elif c1 == Instr.L:
        imp = IMP.L

    elif c1 == Instr.T:
        c2 = inp[ip]
        ip += 1

        if c2 == Instr.S:
            imp = IMP.TS
        elif c2 == Instr.T:
            imp = IMP.TT
        elif c2 == Instr.L:
            imp = IMP.TL
        else:
            raise ValueError

    else:
        raise ValueError

    return imp, ip

class CMD(Enum):
    S = auto()
    T = auto()
    L = auto()
    SS = auto()
    ST = auto()
    SL = auto()
    TS = auto()
    TT = auto()
    TL = auto()
    LS = auto()
    LT = auto()
    LL = auto()

def read_cmd(inp, ip, imp):
    cmd = None

    c1 = inp[ip]
    ip += 1

    if imp == IMP.S:
        if c1 == Instr.S:
            cmd = CMD.S

        elif c1 == Instr.T:
            c2 = inp[ip]
            ip += 1

            if c2 == Instr.S:
                cmd = CMD.TS
            elif c2 == Instr.T:
                raise ValueError
            elif c2 == Instr.L:
                cmd = CMD.TL
            else:
                raise ValueError

        elif c1 == Instr.L:
            c2 = inp[ip]
            ip += 1

            if c2 == Instr.S:
                cmd = CMD.LS
            elif c2 == Instr.T:
                cmd = CMD.LT
            elif c2 == Instr.L:
                cmd = CMD.LL
            else:
                raise ValueError

        else:
            raise ValueError

    elif imp == IMP.L:
        if c1 == Instr.S:
            c2 = inp[ip]
            ip += 1

            if c2 == Instr.S:
                cmd = CMD.SS
            elif c2 == Instr.T:
                cmd = CMD.ST
            elif c2 == Instr.L:
                cmd = CMD.SL
            else:
                raise ValueError

        elif c1 == Instr.T:
            c2 = inp[ip]
            ip += 1

            if c2 == Instr.S:
                cmd = CMD.TS
            elif c2 == Instr.T:
                cmd = CMD.TT
            elif c2 == Instr.L:
                cmd = CMD.TL
            else:
                raise ValueError

        elif c1 == Instr.L:
            c2 = inp[ip]
            ip += 1

            if c2 == Instr.S:
                raise ValueError
            elif c2 == Instr.T:
                raise ValueError
            elif c2 == Instr.L:
                cmd = CMD.LL
            else:
                raise ValueError

        else:
            raise ValueError

    elif imp == IMP.TS:
        if c1 == Instr.S:
            c2 = inp[ip]
            ip += 1

            if c2 == Instr.S:
                cmd = CMD.SS
            elif c2 == Instr.T:
                cmd = CMD.ST
            elif c2 == Instr.L:
                cmd = CMD.SL
            else:
                raise ValueError

        elif c1 == Instr.T:
            c2 = inp[ip]
            ip += 1

            if c2 == Instr.S:
                cmd = CMD.TS
            elif c2 == Instr.T:
                cmd = CMD.TT
            elif c2 == Instr.L:
                raise ValueError
            else:
                raise ValueError

        elif c1 == Instr.L:
            raise ValueError

        else:
            raise ValueError

    elif imp == IMP.TT:
        if c1 == Instr.S:
            cmd = CMD.S
        elif c1 == Instr.T:
            cmd = CMD.T
        elif c1 == Instr.L:
            raise ValueError
        else:
            raise ValueError

    elif imp == IMP.TL:
        if c1 == Instr.S:
            c2 = inp[ip]
            ip += 1

            if c2 == Instr.S:
                cmd = CMD.SS
            elif c2 == Instr.T:
                cmd = CMD.ST
            elif c2 == Instr.L:
                raise ValueError
            else:
                raise ValueError

        elif c1 == Instr.T:
            c2 = inp[ip]
            ip += 1

            if c2 == Instr.S:
                cmd = CMD.TS
            elif c2 == Instr.T:
                cmd = CMD.TT
            elif c2 == Instr.L:
                raise ValueError
            else:
                raise ValueError

        elif c1 == Instr.L:
            raise ValueError

        else:
            raise ValueError

    else:
        raise ValueError

    return cmd, ip

def read_number(inp, ip):
    sign = 0
    if inp[ip] == Instr.S:
        sign = 1
    elif inp[ip] == Instr.T:
        sign = -1
    elif inp[ip] == Instr.L:
        raise ValueError
    else:
        raise ValueError

    ip += 1

    result = 0
    if inp[ip] == Instr.S:
        result = 0
    elif inp[ip] == Instr.T:
        result = 1
    else:
        raise ValueError

    ip += 1

    while inp[ip] != Instr.L:
        if inp[ip] == Instr.S:
            result = result * 2

        elif inp[ip] == Instr.T:
            result = result * 2 + 1

        else:
            raise ValueError

        ip += 1

    ip += 1

    return sign * result, ip

def read_label(inp, ip):
    if inp[ip] == Instr.L:
        raise ValueError

    label = []
    while inp[ip] != Instr.L:
        label.append(inp[ip])
        ip += 1

    return label, ip

def run(inp):
    inp = tokenize(inp)

    # memory
    stack = []
    heap  = {}

    jump_table = {}
    call_stack = []

    ip = 0
    while True:
        imp, ip = read_imp(inp, ip)
        cmd, ip = read_cmd(inp, ip, imp)

        # Stack Manipulation
        if imp == IMP.S:
            if cmd == CMD.S:
                number, ip = read_number(inp, ip)
                stack.append(number)

            elif cmd == CMD.TS:
                # TODO: check order
                number, ip = read_number(inp, ip)
                stack.append(stack[number])

            elif cmd == CMD.TL:
                # TODO: check order
                number, ip = read_number(inp, ip)
                stack = stack[n:]

            elif cmd == CMD.LS:
                top = stack.pop()

                stack.append(top)
                stack.append(top)

            elif cmd == CMD.LT:
                top1 = stack.pop()
                top2 = stack.pop()

                stack.append(top1)
                stack.append(top2)

            elif cmd == CMD.LL:
                stack.pop()

            else:
                raise ValueError

        # Flow Control
        elif imp == IMP.L:
            if cmd == CMD.SS:
                label, ip = read_label(inp, ip)
                jump_table[label] = ip

            elif cmd == CMD.ST:
                label, ip = read_label(inp, ip)

                call_stack.append(ip)
                ip = jump_table[label]

            elif cmd == CMD.SL:
                label, ip = read_label(inp, ip)

                ip = jump_table[label]

            elif cmd == CMD.TS:
                label, ip = read_label(inp, ip)
                top = stack.pop()

                stack.apend(top)
                if top == 0:
                    ip = jump_table[label]

            elif cmd == CMD.TT:
                label, ip = read_label(inp, ip)
                top = stack.pop()

                stack.apend(top)
                if top < 0:
                    ip = jump_table[label]

            elif cmd == CMD.TL:
                caller = call_stack.pop()
                ip = caller

            elif cmd == CMD.LL:
                break

            else:
                raise ValueError

        # Arithmetic
        elif imp == IMP.TS:
            op1 = stack.pop()
            op2 = stack.pop()

            if cmd == CMD.SS:
                stack.append(op1 + op2)

            elif cmd == CMD.ST:
                stack.append(op1 - op2)

            elif cmd == CMD.SL:
                stack.append(op1 * op2)

            elif cmd == CMD.TS:
                stack.append(op1 // op2)

            elif cmd == CMD.TT:
                stack.append(op1 % op2)

            else:
                raise ValueError

        # Heap Access
        elif imp == IMP.TT:
            if cmd == CMD.S:
                value = stack.pop()
                address = stack.pop()

                heap[address] = value

            elif cmd == CMD.T:
                address = stack.pop()

                stack.append(heap[address])

            else:
                raise ValueError

        # I/O
        elif imp == IMP.TL:
            if cmd == CMD.SS:
                top = stack.pop()
                print(chr(top), end='')

            elif cmd == CMD.ST:
                top = stack.pop()
                print(top, end='')

            elif cmd == CMD.TS:
                stack.append(sys.stdin.read(1))

            elif cmd == CMD.TT:
                number = 0
                try:
                    number = int(input())
                except ValueError:
                    pass

                stack.append(number)

            else:
                raise ValueError

        else:
            raise ValueError

def build(inp):
    raise NotImplementedError

def usage(out=sys.stdout):
    out.write("usage: whitespace [mode] [file]\n")

def main():
    if len(sys.argv) != 3:
        usage(sys.stderr)
        exit(1)

    mode = sys.argv[1]
    file = sys.argv[2]

    with open(file, "r") as f:
        src = f.read()

        if mode == "build":
            build(src)
        elif mode == "run":
            run(src)
        else:
            raise ValueError

if __name__ == "__main__":
    main()
