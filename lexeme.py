from enum import Enum, auto
import sys
import re


# Enumeration for lexeme types
class LexType(Enum):
    # Delimiters
    delim_left_brace = auto()
    delim_right_brace = auto()

    delim_left_paren = auto()
    delim_right_paren = auto()

    delim_semicolon = auto()

    # Literals
    lit_number = auto()
    lit_bool = auto()

    # Variables
    var = auto()

    # Keywords
    key_while = auto()

    # Operators
    oprtr_add = auto()
    oprtr_sub = auto()
    oprtr_mul = auto()
    oprtr_div = auto()
    oprtr_eq = auto()

    # EOF and Undefined
    eof = auto()
    und = auto()


# Lexeme (token) class
class Lexeme(object):
    def __init__(self, t, val):
        super().__init__()

        assert(t in LexType)

        self.type = t
        self.val = val

    def __str__(self):
        return str((self.type.name, self.val))

    def __repr__(self):
        return str((self.type.name, self.val))


delim_to_char = {
    LexType.delim_left_brace: '{',
    LexType.delim_right_brace: '}',
    LexType.delim_left_paren: '(',
    LexType.delim_right_paren: ')',
    LexType.delim_semicolon: ';',

    LexType.oprtr_add: '+',
    LexType.oprtr_sub: '-',
    LexType.oprtr_mul: '*',
    LexType.oprtr_div: '/',
    LexType.oprtr_eq: '=',
}

char_to_delim = {v: k for k, v in delim_to_char.items()}


def __is_number(s):
    try:
        float(s)
        return True
    except:
        return False


def __parse_keyword(s):
    if s == "while":
        return True, Lexeme(LexType.key_while, "while")
    if s == "true":
        return True, Lexeme(LexType.lit_bool, True)
    if s == "false":
        return True, Lexeme(LexType.lit_bool, False)

    return False, None


def __parse_string(s):
    assert(s and s != "")

    # Is this a keyword?
    ret, result = __parse_keyword(s)
    if ret:
        return True, result

    # Is this literal (number) ?
    if __is_number(s):
        if s.find('.') != -1 \
                or s.find('e') != -1:
            s = float(s)
        else:
            s = int(s)
        return True, Lexeme(LexType.lit_number, s)

    # Then this should be a variable (identifier)
    if not re.match(r"[a-zA-Z_][0-9a-zA-Z_]*", s):
        print("lx: Invalid identifier: ", s, file=sys.stderr)
        return False, None

    return True, Lexeme(LexType.var, s)


def tokenizer(in_str):
    tokens = []

    # Removing all the whitespaces
    in_str = "".join(in_str.split())
    input_len = len(in_str)
    cur_pos = 0
    cur_string = ""

    while cur_pos < input_len:
        cur_char = in_str[cur_pos]

        if cur_char in char_to_delim:
            if cur_string != "":
                ret, result = __parse_string(cur_string)
                if not ret:
                    return False, []
                tokens.append(result)
                cur_string = ""
            tokens.append(Lexeme(char_to_delim[cur_char], cur_char))
        else:
            cur_string += cur_char

        cur_pos += 1

    # Deal with the remaining string
    if cur_string != "":
        ret, result = __parse_string(cur_string)
        if not ret:
            return False, []
        tokens.append(result)

    return True, tokens

