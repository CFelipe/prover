import re
import argparse
import sys

def is_term(t):
    return re.match(r"[A-Z]+[0-9]*", t) is not None

class Node():
    def __init__(self):
        self.children = []
        self.data = None

class Parser():
    def __init__(self, formula):
        # Taken from Norvig's "(How to Write a (Lisp) Interpreter (in Python))"
        self.tokens = formula.replace('(', ' ( ').replace(')', ' ) ').split()
        self.op_stack = []
        self.out_stack = []
        self.idx = 0

    def peek(self, i = 0):
        if self.idx + i < len(self.tokens):
            print(self.tokens[self.idx + i])
            return self.tokens[self.idx + i]

    def consume(self):
        self.idx = self.idx + 1

    def formula(self):
        for token in self.tokens:
            print(self.out_stack)
            print(self.op_stack)
            print('---')

            if is_term(token):
                self.out_stack.append(token)
            elif token == '-':
                self.op_stack.append(token)
            elif token in ['<=>',
                            '=>',
                            '|',
                            '&']:
                self.op_stack.append(token)
            elif token == '(':
                self.op_stack.append(token)
            elif token == ')':
                while self.op_stack and self.op_stack[-1] != '(':
                    self.out_stack.append(self.op_stack.pop())

                if self.op_stack:
                    if self.op_stack[-1] == '-':
                        self.out_stack.append(self.op_stack.pop())
                    self.op_stack.pop()
                else:
                    print("Mismatched parenthesis")
                    return
            else:
                print("Invalid token:", token)
                return

        while self.op_stack:
            if self.op_stack[-1] != '(':
                self.out_stack.append(self.op_stack.pop())
            else:
                print("Mismatched parenthesis")
                return

        return self.out_stack

def main(argv=None):
    if argv:
        astr = argv[0]

    rpn = Parser(astr).formula()
    rpn_stack = []
    print(rpn)

    result = []

    for token in rpn:
        if is_term(token):
            rpn_stack.append(token)
        else:
            if token == '-':
                op = rpn_stack.pop()
            elif token == '|':
                op1 = rpn_stack.pop()
                op2 = rpn_stack.pop()
            elif token == '=>':
                op1 = rpn_stack.pop()
                op2 = rpn_stack.pop()
            elif token == '<=>':
                op1 = rpn_stack.pop()
                op2 = rpn_stack.pop()

if __name__ == "__main__":
    main(sys.argv[1:])
