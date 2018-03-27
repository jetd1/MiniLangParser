import lexeme
from grammar import check_grammar
from anytree import RenderTree
from anytree.exporter import DotExporter
import matplotlib.pyplot as plt
import sys

if len(sys.argv) > 2:
    print("Reading from %s:" % sys.argv[1])
    in_str = open(sys.argv[1], 'r').read()
else:
    print("Reading (one) line from stdin:")
    in_str = input()
ret, tokens = lexeme.tokenizer(in_str)

if not ret:
    print("lx: Lexemes parse failed")
    exit(-1)
print("lx: Lexemes parse successfully")
print(tokens)
print('\n')


ret, tree = check_grammar(tokens)

if not ret:
    print("gr: Syntactic analysis failed")
    exit(-1)
print("gr: Syntactic analysis successfully")


for pre, fill, node in RenderTree(tree):
    print("%s%s" % (pre, node.name))


def name_func_gen():
    l = {}
    cnt = 0

    def name_func(node):
        nonlocal cnt
        if str(id(node)) not in l:
            l[str(id(node))] = cnt
            cnt += 1
        return node.name + ' (id=' + str(l[str(id(node))]) + ')'

    return name_func

if len(sys.argv) > 2:
    DotExporter(tree, nodenamefunc=name_func_gen()).to_picture(sys.argv[2])
    img = plt.imread(sys.argv[2])
    plt.imshow(img)
    plt.show()

