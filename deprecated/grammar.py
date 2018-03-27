from lexeme import Lexeme, LexType
import sys
import copy


class GrammarTree(object):
    def __init__(self, data=None):
        super().__init__()
        self.data = data
        self.children = []

    def print(self, beg=''):
        print(beg + self.data)
        beg += '    '
        for node in self.children:
            node.print(beg=beg)

# Alias for GrammarTree
Node = GrammarTree


def check_grammar(tokens):
    assert(isinstance(tokens, list))

    # Empty sequence
    if len(tokens) == 0:
        print("gr: Empty token sequence!", file=sys.stderr)
        return False

    # Ending guard
    tokens.append(Lexeme(LexType.eof, "eof"))

    # Iterative token getter:
    # Use inner function `next_token`
    # to get the next token
    cur_idx = 0
    cur_tok = Lexeme(LexType.und, "undef")

    def next_token():
        nonlocal cur_idx, cur_tok
        if cur_tok is None:
            raise RuntimeError("gr: Unexpected ending")
        cur_tok = tokens[cur_idx]
        cur_idx += 1

    # Grammar parsers
    def statements(cur_node):
        nonlocal cur_tok, cur_idx

        if cur_tok.type == LexType.eof:
            cur_node.children.append(Node("ε"))
            return True

        # Backup
        org_idx = cur_idx
        org_tok = copy.copy(cur_tok)

        statement_node = Node("statement")
        cur_node.children.append(statement_node)
        if not statement(statement_node):
            cur_idx = org_idx
            cur_tok = org_tok
            statement_node.children.pop()
            cur_node.children.append(Node("ε"))
            return True

        statements_node = Node("statements")
        cur_node.children.append(statements_node)
        return statements(statements_node)

    def statement(cur_node):
        nonlocal cur_tok

        if cur_tok.type == LexType.delim_semicolon:
            cur_node.children.append(Node(cur_tok.val))
            next_token()
            return True

        if cur_tok.type == LexType.key_while:
            while_clause_node = Node("while_clause")
            cur_node.children.append(while_clause_node)
            return while_clause(while_clause_node)

        expr_node = Node("expr")
        cur_node.children.append(expr_node)
        if not expr(expr_node):
            return False

        if cur_tok.type != LexType.delim_semicolon:
            return False
        cur_node.children.append(Node(cur_tok.val))
        next_token()
        return True

    def while_clause(cur_node):
        nonlocal cur_tok
        cur_node.data = "while_clause"

        if cur_tok.type != LexType.key_while:
            return False
        cur_node.children.append(Node("while"))
        next_token()

        if cur_tok.type != LexType.delim_left_paren:
            return False
        cur_node.children.append(Node(cur_tok.val))
        next_token()

        expr_node = Node("expr")
        cur_node.children.append(expr_node)
        if not expr(expr_node):
            return False

        if cur_tok.type != LexType.delim_right_paren:
            return False
        cur_node.children.append(Node(cur_tok.val))
        next_token()

        while_body_node = Node("while_body")
        cur_node.children.append(while_body_node)
        return while_body(while_body_node)

    def while_body(cur_node):
        nonlocal cur_tok

        if cur_tok.type == LexType.delim_semicolon:
            cur_node.children.append(Node(cur_tok.val))
            next_token()
            return True
        elif cur_tok.type == LexType.delim_left_brace:
            cur_node.children.append(Node(cur_tok.val))
            next_token()

            statements_node = Node("statements")
            cur_node.children.append(statements_node)
            if not statements(statements_node):
                return False
            if cur_tok.type != LexType.delim_right_brace:
                return False
            cur_node.children.append(Node(cur_tok.val))
            next_token()
            return True
        else:
            expr_node = Node("expr")
            cur_node.children.append(expr_node)
            if not expr(expr_node):
                return False
        if cur_tok.type != LexType.delim_semicolon:
            return False
        cur_node.children.append(Node(cur_tok.val))
        next_token()
        return True

    def expr(cur_node):
        nonlocal cur_tok, cur_idx

        # Look forward for 2
        if cur_tok.type == LexType.var \
                and tokens[cur_idx].type == LexType.oprtr_eq:
            cur_node.children.append(Node(cur_tok.type.name + ': '
                                          + str(cur_tok.val)))
            next_token()
            cur_node.children.append(Node(cur_tok.val))
            next_token()

            expr_node = Node("expr")
            cur_node.children.append(expr_node)
            return expr(expr_node)

        rexpr_node = Node("rexpr")
        cur_node.children.append(rexpr_node)
        return rexpr(rexpr_node)

    def rexpr(cur_node):
        nonlocal cur_tok

        term_node = Node("term")
        cur_node.children.append(term_node)
        if not term(term_node):
            return False

        rexpr_tail_node = Node("rexpr_tail")
        cur_node.children.append(rexpr_tail_node)
        return rexpr_tail(rexpr_tail_node)

    def term(cur_node):
        nonlocal cur_tok

        factor_node = Node("factor")
        cur_node.children.append(factor_node)
        if not factor(factor_node):
            return False

        term_tail_node = Node("term_tail")
        cur_node.children.append(term_tail_node)
        return term_tail(term_tail_node)

    def rexpr_tail(cur_node):
        nonlocal cur_tok

        if cur_tok.type == LexType.oprtr_add \
                or cur_tok.type == LexType.oprtr_sub:
            cur_node.children.append(Node(cur_tok.val))
            next_token()

            term_node = Node("term")
            cur_node.children.append(term_node)
            if not term(term_node):
                return False
            rexpr_tail_node = Node("rexpr_tail")
            cur_node.children.append(rexpr_tail_node)
            return rexpr_tail(rexpr_tail_node)

        cur_node.children.append(Node("ε"))
        return True

    def factor(cur_node):
        nonlocal cur_tok

        if cur_tok.type == LexType.var \
                or cur_tok.type == LexType.lit_bool \
                or cur_tok.type == LexType.lit_number:
            cur_node.children.append(Node(cur_tok.type.name + ': '
                                          + str(cur_tok.val)))
            next_token()
            return True

        if cur_tok.type != LexType.delim_left_paren:
            return False
        cur_node.children.append(Node(cur_tok.val))
        next_token()

        rexpr_node = Node("rexpr")
        cur_node.children.append(rexpr_node)
        if not rexpr(rexpr_node):
            return False

        if cur_tok.type != LexType.delim_right_paren:
            return False
        cur_node.children.append(Node(cur_tok.val))
        next_token()
        return True

    def term_tail(cur_node):
        nonlocal cur_tok

        if cur_tok.type == LexType.oprtr_mul \
                or cur_tok.type == LexType.oprtr_div:
            cur_node.children.append(Node(cur_tok.val))
            next_token()

            factor_node = Node("factor")
            cur_node.children.append(factor_node)
            if not factor(factor_node):
                return False

            term_tail_node = Node("term_tail")
            cur_node.children.append(term_tail_node)
            return term_tail(term_tail_node)

        cur_node.children.append(Node("ε"))
        return True

    # Initialize the first token
    next_token()

    # Yet-to-be-built grammar tree
    tree = GrammarTree("statements")

    if not statements(tree):
        return False, None

    if cur_tok.type != LexType.eof:
        print("gr: Trailing texts", file=sys.stderr)
        return False, None

    return True, tree

