from lexeme import Lexeme, LexType
import sys
import copy
import anytree


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
    err = False

    def next_token():
        nonlocal cur_idx, cur_tok
        cur_tok = tokens[cur_idx]
        cur_idx += 1

    def no_err():
        nonlocal err
        return not err

    def set_err():
        nonlocal err
        err = True

    # Grammar parsers
    def statements(cur_node):
        nonlocal cur_tok, cur_idx

        if cur_tok.type == LexType.eof \
                or cur_tok.type == LexType.delim_right_brace:
            anytree.Node("ε", parent=cur_node)
            return no_err()

        # Backup
        org_idx = cur_idx
        org_tok = copy.copy(cur_tok)

        statement_node = anytree.Node("statement", parent=cur_node)
        if not statement(statement_node):
            cur_idx = org_idx
            cur_tok = org_tok
            statement_node.parent = None
            anytree.Node("ε", parent=cur_node)
            return no_err()

        statements_node = anytree.Node("statements", parent=cur_node)
        return statements(statements_node)

    def statement(cur_node):
        nonlocal cur_tok

        if cur_tok.type == LexType.delim_semicolon:
            anytree.Node(cur_tok.val, parent=cur_node)
            next_token()
            return no_err()

        if cur_tok.type == LexType.key_while:
            while_clause_node = anytree.Node("while_clause", parent=cur_node)
            return while_clause(while_clause_node)

        expr_node = anytree.Node("expr", parent=cur_node)
        if not expr(expr_node):
            return False

        if cur_tok.type != LexType.delim_semicolon:
            set_err()
            assert (cur_idx > 1)
            print("gr: Expect ';' after lexeme",
                  tokens[cur_idx - 2].val, file=sys.stderr)
            return False
        anytree.Node(cur_tok.val, parent=cur_node)
        next_token()
        return no_err()

    def while_clause(cur_node):
        nonlocal cur_tok, cur_idx

        if cur_tok.type != LexType.key_while:
            return False
        anytree.Node("while", parent=cur_node)
        next_token()

        if cur_tok.type != LexType.delim_left_paren:
            set_err()
            print("gr: Expect '(' after keyword 'while'", file=sys.stderr)
            return False
        anytree.Node(cur_tok.val, parent=cur_node)
        next_token()

        expr_node = anytree.Node("expr", parent=cur_node)
        if not expr(expr_node):
            set_err()
            print("gr: Invalid expression after 'while ('", file=sys.stderr)
            return False

        if cur_tok.type != LexType.delim_right_paren:
            set_err()
            assert(cur_idx > 1)
            print("gr: Expect ')' after lexeme",
                  tokens[cur_idx - 2].val, file=sys.stderr)
            return False
        anytree.Node(cur_tok.val, parent=cur_node)
        next_token()

        while_body_node = anytree.Node("while_body", parent=cur_node)
        return while_body(while_body_node)

    def while_body(cur_node):
        nonlocal cur_tok

        if cur_tok.type == LexType.delim_left_brace:
            anytree.Node(cur_tok.val, parent=cur_node)
            next_token()

            statements_node = anytree.Node("statements", parent=cur_node)
            if not statements(statements_node):
                return False
            if cur_tok.type != LexType.delim_right_brace:
                set_err()
                assert (cur_idx > 1)
                print("gr: Expect '}' after lexeme",
                      tokens[cur_idx - 2].val, file=sys.stderr)
                return False
            anytree.Node(cur_tok.val, parent=cur_node)
            next_token()
            return no_err()
        else:
            statement_node = anytree.Node("statement", parent=cur_node)
            return statement(statement_node)

    def expr(cur_node):
        nonlocal cur_tok, cur_idx

        if cur_tok.type == LexType.eof:
            set_err()
            print("gr: Unexpected eof", file=sys.stderr)
            return False

        # Look forward for 2
        if cur_tok.type == LexType.var \
                and tokens[cur_idx].type == LexType.oprtr_eq:
            anytree.Node(cur_tok.type.name + ': '
                         + str(cur_tok.val), parent=cur_node)
            next_token()
            anytree.Node(cur_tok.val, parent=cur_node)
            next_token()

            expr_node = anytree.Node("expr", parent=cur_node)
            return expr(expr_node)

        rexpr_node = anytree.Node("rexpr", parent=cur_node)
        return rexpr(rexpr_node)

    def rexpr(cur_node):
        nonlocal cur_tok

        term_node = anytree.Node("term", parent=cur_node)
        if not term(term_node):
            return False

        rexpr_tail_node = anytree.Node("rexpr_tail", parent=cur_node)
        return rexpr_tail(rexpr_tail_node)

    def term(cur_node):
        nonlocal cur_tok

        factor_node = anytree.Node("factor", parent=cur_node)
        if not factor(factor_node):
            return False

        term_tail_node = anytree.Node("term_tail", parent=cur_node)
        return term_tail(term_tail_node)

    def rexpr_tail(cur_node):
        nonlocal cur_tok

        if cur_tok.type == LexType.oprtr_add \
                or cur_tok.type == LexType.oprtr_sub:
            anytree.Node(cur_tok.val, parent=cur_node)
            next_token()

            term_node = anytree.Node("term", parent=cur_node)
            if not term(term_node):
                return False
            rexpr_tail_node = anytree.Node("rexpr_tail", parent=cur_node)
            return rexpr_tail(rexpr_tail_node)

        anytree.Node("ε", parent=cur_node)
        return no_err()

    def factor(cur_node):
        nonlocal cur_tok

        if cur_tok.type == LexType.var \
                or cur_tok.type == LexType.lit_bool \
                or cur_tok.type == LexType.lit_number:
            anytree.Node(cur_tok.type.name + ': '
                         + str(cur_tok.val), parent=cur_node)
            next_token()
            return no_err()

        if cur_tok.type != LexType.delim_left_paren:
            set_err()
            assert (cur_idx > 1)
            print("gr: Expect valid r-expressions after",
                  tokens[cur_idx - 2].val, file=sys.stderr)
            return False
        anytree.Node(cur_tok.val, parent=cur_node)
        next_token()

        rexpr_node = anytree.Node("rexpr", parent=cur_node)
        if not rexpr(rexpr_node):
            return False

        if cur_tok.type != LexType.delim_right_paren:
            set_err()
            assert (cur_idx > 1)
            print("gr: Expect ')' after lexeme",
                  tokens[cur_idx - 2].val, file=sys.stderr)
            return False
        anytree.Node(cur_tok.val, parent=cur_node)
        next_token()
        return no_err()

    def term_tail(cur_node):
        nonlocal cur_tok

        if cur_tok.type == LexType.oprtr_mul \
                or cur_tok.type == LexType.oprtr_div:
            anytree.Node(cur_tok.val, parent=cur_node)
            next_token()

            factor_node = anytree.Node("factor", parent=cur_node)
            if not factor(factor_node):
                return False

            term_tail_node = anytree.Node("term_tail", parent=cur_node)
            return term_tail(term_tail_node)

        anytree.Node("ε", parent=cur_node)
        return no_err()

    # Initialize the first token
    next_token()

    # Yet-to-be-built grammar tree
    tree = anytree.Node("statements")

    if not statements(tree):
        return False, None

    if cur_tok.type != LexType.eof:
        print("gr: Trailing texts", file=sys.stderr)
        return False, None

    if not no_err():
        print("gr: Unknown error", file=sys.stderr)
        return False, None

    return True, tree

