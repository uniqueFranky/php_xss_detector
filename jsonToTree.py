import json
from enum import Enum


# Load the json file into a dictionary and return it
def loadJson(filepath):
    with open(filepath, 'r') as f:
        code = json.load(f)
    return code


useless_tag = ["attributes"]
leaf_tag = ["name", "value", "items"]
mid_tag = ["expr", "var", "left", "right", "dim"]
cannot_sure_tag = [] # cannot sure about its usage
list_tag = ["exprs"]

class Type(Enum):
    LEAF = 1
    NODE = 2
    ROOT = 3

def buildAstTree(dict):
    ast_tree = {}
    ast_tree["children"] = []
    for key, value in dict.items():
        if key == "nodeType":
            ast_tree["nodeName"] = value
        elif key in leaf_tag:
            ast_tree["type"] = Type.LEAF
            ast_tree["children"].append(value) # not actual "child"
        elif key in useless_tag:    
            continue
        elif key in cannot_sure_tag: 
            if type(value) == dict or type(value) != list: 
                print(f"long not sure tag: {key}")
                assert(False)
            ast_tree["type"] = Type.NODE
            ast_tree[key] = value
        elif key in mid_tag:
            ast_tree["type"] = Type.NODE
            # Note: the behavior of None is worth paying attention to
            if value == None and key == "dim":
                ast_tree["children"].append({"type": Type.LEAF, "nodeName": "Array_Dim", "children": ["Array_NextIdx"]})
            else:
                ast_tree["children"].append(buildAstTree(value))
        elif key in list_tag:
            ast_tree["type"] = Type.NODE
            for param in value:
                ast_tree["children"].append(buildAstTree(param))
        else:
            print(f"Unknown tag: {key}")
            assert(False)

    return ast_tree

def print_tree(root):
    print("The Ast tree generated is as folloed:\n")
    traverse_and_print(root, 0)    

def traverse_and_print(tree, indent):
    for _ in range(indent):
        print(" ", end="")
    if tree["type"] == Type.LEAF:
        print(f"{tree['nodeName']} ---> {tree['children'][0]}")
    else:
        print(f"{tree['nodeName']}")
        for child in tree["children"]:
            traverse_and_print(child, indent + 1)

ast_tree = {}
ast_tree["type"], ast_tree["nodeName"], ast_tree["children"] = Type.ROOT, "CodeStart", []
filepath = "ast.json"
dict = loadJson(filepath)
for code_line in dict:
    ast_tree["children"].append(buildAstTree(code_line))
print_tree(ast_tree)
