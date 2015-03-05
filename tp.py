import re
import argparse
import sys

def is_op(t):
    return t in ["<=>", "=>", "|", "&"]

def is_term(t):
    return re.match(r"[A-Z]+[0-9]*", t) is not None

def print_tree(node, level = 0):
    if node is not None:
        print("." * 4 * level + node.root)
        for n in node.children:
            print_tree(n, level + 1)

class Node(object):
    def __init__(self, root, children=[]):
        if type(root) == str:
            self.root = root
            self.children = children
        elif type(root) == Node:
            self.root = root.root
            self.children = root.children
        elif type(root) == list:
            self.root = root.root
            self.children = root.children

    def __repr__(self):
        return "{R: " + self.root + ", C: " + str(self.children) + "}"

def parse(astr):
    # Taken from Norvig's "(How to Write a (Lisp) Interpreter (in Python))"
    tokens = astr.replace("(", " ( ") \
                 .replace(")", " ) ") \
                 .replace("-", " - ") \
                 .split()
    op_stack = []
    out_stack = []

    for token in tokens:
        print(token)
        print(out_stack)
        print(op_stack)
        print("---")

        if is_term(token):
            out_stack.append(token)
        elif token == "-":
            op_stack.append(token)
        elif is_op(token):
            while op_stack and op_stack[-1] == "-":
                try:
                    out_stack.append(Node(op_stack.pop(),
                                            [Node(out_stack.pop())]))
                except:
                    print("Invalid format")
                    return

            op_stack.append(token)

        elif token == "(":
            op_stack.append(token)
        elif token == ")":
            while op_stack and op_stack[-1] != "(":
                if op_stack[-1] == "-":
                    try:
                        out_stack.append(Node(op_stack.pop(),
                                              [Node(out_stack.pop())]))
                    except:
                        print("Invalid format")
                        return

                else:
                    try:
                        print(op_stack)
                        print(out_stack)
                        out_stack.append(Node(op_stack.pop(),
                                             [Node(out_stack.pop()),
                                              Node(out_stack.pop())][::-1]))
                    except:
                        print("Invalid format")
                        return

            if op_stack:
                op_stack.pop()
            else:
                print("Mismatched parenthesis")
                return
        else:
            print("Invalid token:", token)
            return

    while op_stack:
        if op_stack[-1] != '(':
            out_stack.append(op_stack.pop())
        else:
            print("Mismatched parenthesis")
            return

    if len(out_stack) == 1:
        return out_stack[0]
    else:
        print("Invalid format")
        return

def trav1(node):
    if node.root == "=>":
        node.root = "|"
        node.children[0] = Node("-", [Node(node.children[0])])
    elif node.root == "<=>":
        node.root = "&"
        node.children = [Node("|", [Node("-", [node.children[0]]), Node(node.children[1])]),
                            Node("|", [Node("-", [node.children[1]]), Node(node.children[0])])]

    for n in node.children:
        trav1(n)

def trav2(node):
    if node.root == "-":
        ch = node.children[0]
        if not is_term(ch.root):
            if ch.root == "-":
                new_node = Node(ch.children[0])
                node.root = new_node.root
                node.children = new_node.children
            elif ch.root == "|":
                new_node = Node("&", [Node("-", [ch.children[0]]), Node("-", [ch.children[1]])])
                node.root = new_node.root
                node.children = new_node.children
            elif ch.root == "&":
                new_node = Node("|", [Node("-", [ch.children[0]]), Node("-", [ch.children[1]])])
                node.root = new_node.root
                node.children = new_node.children

    for n in node.children:
        trav2(n)

def cnfize(ast):
    trav1(ast)
    trav2(ast)

def main(argv=None):
    if argv:
        astr = argv[0]

    ast = parse(astr)
    print(ast)
    print_tree(ast)
    cnfize(ast)
    print(ast)
    print_tree(ast)

if __name__ == "__main__":
    main(sys.argv[1:])
