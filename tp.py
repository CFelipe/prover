import re
import argparse
import sys

# Helpers ---------------------------------------------------------------------

class ParseException(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg

# From https://groups.google.com/forum/#!topic/argparse-users/LazV_tEQvQw
class ArgParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

def print_header(text):
    print("\n", "-" * len(text), sep = "")
    print(text)
    print("-" * len(text), "\n", sep = "")

def is_op(t):
    return t in ["<=>", "=>", "|", "&"]

def is_term(t):
    return re.match(r"[A-Z]+[0-9]*", t) is not None

def print_tree(node, level = 0):
    if node is not None:
        print("." * 4 * level + node.root)
        for n in node.children:
            print_tree(n, level + 1)

def negation(term):
    if term[0] == "-":
        return term[1:]
    else:
        return "-" + term

def longest_term(clauses):
    longest = 0
    for clause in clauses:
        for term in clause:
            if len(term) > longest: longest = len(term)
    return longest

def print_clauses(clauses, c1=None, c2=None):
    print("{")
    w = longest_term(clauses)
    for clause in clauses:
        sorted_clauses = sorted(clause,
                                key = lambda x: x[1:] if x[0] == "-" else x)
        prefix = "{}{}{{".format(">" if clause == c1 else " ",
                                 ">" if clause == c2 else " ")
        print(prefix,
              ", ".join("{0:>{1}}".format(x, w) for x in sorted_clauses),
              "}",
              sep = "")
    print("}")

def save_cnf(clauses, filename):
    clause_dict = {}
    count = 0
    output = []

    for clause in clauses:
        line = ''
        for term in clause:
            term_val = term[1:] if term[0] == "-" else term
            if term_val not in clause_dict:
                count += 1
                clause_dict[term_val] = count
                line += ("-" if term[0] == "-" else "") + \
                        str(count) + " "
            else:
                line += ("-" if term[0] == "-" else "") + \
                        str(clause_dict[term_val]) + " "
        output.append(line + '0')
    output = "\n".join(output)
    output = " ".join(["p cnf",
                       str(len(clause_dict)),
                       str(len(clauses))]) + "\n" + output

    with open(filename, 'w') as f:
        f.write(output)

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

# Procedures ------------------------------------------------------------------

def parse(astr, output):
    # Taken from Norvig's "(How to Write a (Lisp) Interpreter (in Python))"
    tokens = astr.replace("(", " ( ") \
                 .replace(")", " ) ") \
                 .replace("->", "=>") \
                 .replace("<->", "<=>") \
                 .replace("-", " - ") \
                 .split()
    tokens.insert(0, "(")
    tokens.append(")")
    op_stack = []
    out_stack = []

    for token in tokens:
        if output:
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
                    if output:
                        print(op_stack)
                        print(out_stack)
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
                        if output:
                            print(op_stack)
                            print(out_stack)
                        out_stack.append(Node(op_stack.pop(),
                                              [Node(out_stack.pop())]))
                    except:
                        raise ParseException("Invalid format")
                else:
                    try:
                        if output:
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
            if output:
                print(op_stack)
                print(out_stack)
            out_stack.append(op_stack.pop())
        else:
            raise ParseException("Mismatched parenthesis")

    if len(out_stack) == 1:
        if type(out_stack[0]) == str:
            if output:
                print(op_stack)
                print(out_stack)
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
    elif is_term(node.root) or node.root[0] == "-":
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

def optimise(clauses, subsume=False, order=False):
    # Try to resolve smaller clauses first
    if order:
        print_header("Ordering")
        clauses = sorted(clauses, key=len)
        print_clauses(clauses)


    # Subsumption
    if subsume:
        for i, c1 in enumerate(sorted(clauses)):
            for c2 in sorted(clauses)[i + 1:]:
                print(c1, c2)
                if c1.issubset(c2) and c1 != c2:
                    print("\nSubsumption step")
                    print("c1:", c1, " | ", "c2:", c2)
                    clauses.remove(c2)

def resolve(clauses):
    for i, c1 in enumerate(clauses):
        for t1 in c1:
            for c2 in clauses[i:]:
                for t2 in c2:
                    if negation(t1) == t2:
                        resolvent = c1.union(c2).difference({t1, t2})
                        if resolvent not in clauses:
                            print_clauses(clauses, c1, c2)
                            print()
                            print("T1:", t1, "|",
                                  "T2:", t2, "|",
                                  "R:", resolvent if resolvent != set()
                                                  else "{}")
                            print()
                            print("--------------")
                            print()
                            clauses.append(resolvent)
                            if(len(c1) > 1): clauses.remove(c1)
                            if c1 != c2 and len(c2) > 1: clauses.remove(c2)

                            if resolvent == set():
                                return "Unsatisfiable"
                            else:
                                return(resolve(clauses))
    return "Satisfiable"


def main(argv=None):
    parser = ArgParser(description="Automated theorem prover")
    parser.add_argument('formula',
                        help="a logic formula")
    parser.add_argument('-s',
                        action="store_true",
                        help="use subsumption")
    parser.add_argument('-o',
                        action="store_true",
                        help="use unit preference")
    parser.add_argument('-r',
                        action="store_true",
                        help="use set of support")
    parser.add_argument('-p',
                        action="store_true",
                        help="show parsing steps")
    parser.add_argument('--cnf',
                        action="store_true",
                        help="output CNF and exit")
    parser.add_argument('--save',
                        nargs="?",
                        const="cnf",
                        metavar="filename",
                        help="save CNF in DIMACS format")
    args = parser.parse_args()
    print(args)

    if args.p: print_header("Parsing")
    ast = parse(args.formula, args.p)
    print_header("AST")
    print_tree(ast)
    print_header("CNF tree")
    clauses = cnfize(ast)
    print_tree(ast)
    print_header("Clauses")
    print_clauses(clauses)
    optimise(clauses, args.s, args.o)

    if args.save:
        save_cnf(clauses, args.save + ".cnf")

    if not args.cnf:
        print_header("Resolution")
        print(resolve(clauses))

if __name__ == "__main__":
    main(sys.argv[1:])
