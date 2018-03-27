import lexeme
from grammar import check_grammar


in_str = input()
ret, tokens = lexeme.tokenizer(in_str)

if not ret:
    print("lx: Lexicons parse failed")
    exit(-1)
print("lx: Lexicons parse successfully")
print(tokens)


ret, tree = check_grammar(tokens)

if not ret:
    print("gr: Grammar analysis failed")
    exit(-1)
print("gr: Grammar analysis successfully")
tree.print()
