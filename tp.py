import re
import argparse
import sys

class ParseException(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg

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
    tokens.insert(0, "(")
    tokens.append(")")
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
                    raise ParseException("Invalid format")

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
                        raise ParseException("Invalid format")
                else:
                    try:
                        print(op_stack)
                        print(out_stack)
                        out_stack.append(Node(op_stack.pop(),
                                             [Node(out_stack.pop()),
                                              Node(out_stack.pop())][::-1]))
                    except:
                        raise ParseException("Invalid format")

            if op_stack:
                op_stack.pop()
            else:
                raise ParseException("Mismatched parenthesis")
        else:
            raise ParseException("Invalid token: "+ token)

    while op_stack:
        if op_stack[-1] != '(':
            out_stack.append(op_stack.pop())
        else:
            raise ParseException("Mismatched parenthesis")

    if len(out_stack) == 1:
        if type(out_stack[0]) == str:
            out_stack.append(Node(out_stack.pop(), []))
        return out_stack[0]
    else:
        raise ParseException("Invalid format")

def trav1(node):
    """Equivalence and implication"""

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
    """De Morgan and Double Negation"""

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

def trav3(node):
    """Distributivity disjunction"""

    if node.root == "|":
        ch = node.children
        if ch[0].root == '&':
            new_node = Node("&", [Node('|', [Node(ch[1]), Node(ch[0].children[0])]),
                                  Node('|', [Node(ch[1]), Node(ch[0].children[1])])])
            node.root = new_node.root
            node.children = new_node.children
            trav3(node)
        elif ch[1].root == '&':
            new_node = Node("&", [Node('|', [Node(ch[0]), Node(ch[1].children[0])]),
                                  Node('|', [Node(ch[0]), Node(ch[1].children[1])])])
            node.root = new_node.root
            node.children = new_node.children
            trav3(node)

    for n in node.children:
        trav3(n)

def clauses(node, sets=[]):
    if node.root == "&":
        for n in node.children:
            clauses(n, sets)
    elif node.root == "|":
        l = set()
        for n in node.children:
            add_clause(n, l)
        if l not in sets: sets.append(l)
    elif is_term(node.root):
        l = set()
        add_clause(node, l)
        if l not in sets: sets.append(l)

    return sets

def add_clause(node, clauses):
    if is_term(node.root):
        clauses.add(node.root)
    elif node.root == "-":
        neg = "-" + node.children[0].root
        clauses.add(neg)
    elif node.root == "|":
        for n in node.children:
            add_clause(n, clauses)
    else:
        print(type(node.root))
        print(node.root)

def cnfize(ast):
    trav1(ast)
    trav2(ast)
    trav3(ast)

    return clauses(ast)

def negation(term):
    if term[0] == "-":
        return term[1:]
    else:
        return "-" + term

def resolve(clauses):
    changed = True
    while changed:
        print('---')
        changed = False
        clauses = sorted(clauses, key=len)
        print(clauses)
        for i, c1 in enumerate(clauses):
            for t1 in c1:
                for c2 in clauses[i:]:
                    for t2 in c2:
                        if negation(t1) == t2:
                            resolvent = c1.union(c2).difference({t1, t2})
                            if resolvent == set():
                                return True
                            print("Resolvent", resolvent)
                            if resolvent not in clauses:
                                clauses.append(resolvent)
                                changed = True

def main(argv=None):
    if argv:
        astr = argv[0]
        ast = parse(astr)
        print("AST")
        print_tree(ast)
        print("CNFized")
        clauses = cnfize(ast)
        print_tree(ast)
        print(clauses)
        print(resolve(clauses))

if __name__ == "__main__":
    main(sys.argv[1:])
