#!/bin/python
import os
import sys
import subprocess

cmds = [ ">", "<", "+", "-", ".", ",", "[", "]" ]

def validate_brackets(string):
    stack = []

    for c in string:
        if c == "[":
            stack.append(c)
        elif c == "]":
            if len(stack) == 0:
                return false

            p = stack.pop()
            if p != "[":
                return false

    return len(stack) == 0

def pair_brackets(string):
    stack = []
    r = {}

    for i, c in enumerate(string):
        if c == "[":
            stack.append(i)
        elif c == "]":
            pi = stack.pop()
            r[i]  = pi
            r[pi] = i

    return r

def run(program):
    program = list(filter(lambda c: c in cmds, program))

    if not validate_brackets(program):
        return

    table = pair_brackets(program)

    buff = [0] * 30000
    ptr = 0
    ip = 0

    while ip < len(program):
        op = program[ip]

        if op == ">":
            ptr += 1
            ip += 1

        elif op == "<":
            ptr -= 1
            ip += 1

        elif op == "+":
            buff[ptr] += 1
            ip += 1

        elif op == "-":
            buff[ptr] -= 1
            ip += 1

        elif op == ".":
            print(chr(buff[ptr]), end="")
            ip += 1

        elif op == ",":
            read = sys.stdin.read(1)
            if read != '':
                buff[ptr] = ord(read)
            else:
                exit(1)

            ip += 1

        elif op == "[":
            if buff[ptr] == 0:
                ip = table[ip] + 1
            else:
                ip += 1
            
        elif op == "]":
            ip = table[ip]

        else:
            ip += 1

def build(program, out):
    program = list(filter(lambda c: c in cmds, program))
    if not validate_brackets(program):
        return

    table = pair_brackets(program)

    out.write("BITS 64\n\n")

    out.write("segment .bss\n")
    out.write("buffer: resb 30000\n\n")

    out.write("segment .text\n")

    out.write("print:\n")
    out.write("    mov rsi, rdi\n")
    out.write("    mov edx, 1\n")
    out.write("    mov edi, 1\n")
    out.write("    mov rax, 1\n") # 'write' syscall
    out.write("    syscall\n")
    out.write("    ret\n\n")

    out.write("read:\n")
    out.write("    mov rsi, rdi\n")
    out.write("    mov edx, 1\n")
    out.write("    mov edi, 0\n")
    out.write("    mov rax, 0\n") # 'read' syscall
    out.write("    syscall\n")
    out.write("    ret\n\n")

    out.write("global _start\n")
    out.write("_start:\n")
    out.write("    mov QWORD rbp, buffer\n")

    for ip in range(len(program)):
        op = program[ip]
        out.write(f"addr_{ip}:\n")

        if op == ">":
            out.write("    add QWORD rbp, 1\n")

        elif op == "<":
            out.write("    sub QWORD rbp, 1\n")

        elif op == "+":
            out.write("    mov   rax, QWORD rbp\n")
            out.write("    movzx eax, BYTE [rax]\n")
            out.write("    add   eax, 1\n")
            out.write("    mov   edx, eax\n")
            out.write("    mov   rax, QWORD rbp\n")
            out.write("    mov   BYTE [rax], dl\n")

        elif op == "-":
            out.write("    mov   rax, QWORD rbp\n")
            out.write("    movzx eax, BYTE [rax]\n")
            out.write("    sub   eax, 1\n")
            out.write("    mov   edx, eax\n")
            out.write("    mov   rax, QWORD rbp\n")
            out.write("    mov   BYTE [rax], dl\n")

        elif op == ".":
            out.write("    mov  rdi, rbp\n");
            out.write("    call print\n");

        elif op == ",":
            out.write("    mov  rdi, rbp\n");
            out.write("    call read\n");

        elif op == "[":
            out.write("    mov rax, QWORD rbp\n")
            out.write("    movzx eax, BYTE [rax]\n")
            out.write("    cmp eax, 0\n")
            out.write(f"    jle addr_{table[ip]+1}\n")
                
        elif op == "]":
            out.write(f"    jmp addr_{table[ip]}\n")

    out.write(f"addr_{len(program)}:\n")
    out.write("    mov rax, 60\n")
    out.write("    mov rdi, 1\n")
    out.write("    syscall\n")

def usage(out):
    out.write("usage: ./brainfuck <mode> <file>\n")

def cmd_echo(cmd):
    print(f"[CMD] {' '.join(cmd)}")
    return subprocess.call(cmd)

def main():
    if len(sys.argv) != 3:
        usage(sys.stderr)
        exit(1)

    mode = sys.argv[1]
    file = sys.argv[2]

    if not file.endswith(".bf"):
        usage(sys.stderr)
        exit(1)

    basename = file.rsplit(".", 1)[0]
    source   = open(file, "r").read()

    if sys.argv[1] == "run":
        run(source)

    elif sys.argv[1] == "build":
        build(source, open(f"{basename}.asm", "w"))

        cmd_echo(["nasm", "-felf64", f"{basename}.asm"])
        cmd_echo(["ld", "-o", basename, f"{basename}.o"])
        cmd_echo(["rm", f"{basename}.asm", f"{basename}.o"])

    else:
        usage(sys.stderr)
        exit(1)

if __name__ == "__main__":
    main()
