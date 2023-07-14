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


def buildAstTree(dict: dict, parent: dict): 
    """
    given the json data(stored in dictionary), build the AST
    Test the code with:
        ast_tree = {}
        ast_tree["type"], ast_tree["nodeName"], ast_tree["children"] = Type.ROOT, "CodeStart", []
        filepath = "ast.json"
        dict = loadJson(filepath)
        for code_line in dict:
            ast_tree["children"].append(buildAstTree(code_line, ast_tree))
        print("The Ast tree generated is as folloed:\n")
        traverse_and_print(ast_tree, 0)
    """
    ast_tree = {}
    ast_tree["children"] = []
    ast_tree["parent"] = parent
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
                ast_tree["children"].append({"type": Type.LEAF, "nodeName": "Array_Dim", "children": ["Array_NextIdx"], "parent": ast_tree})
            else:
                ast_tree["children"].append(buildAstTree(value, ast_tree))
        elif key in list_tag:
            ast_tree["type"] = Type.NODE
            for param in value:
                ast_tree["children"].append(buildAstTree(param, ast_tree))
        else:
            print(f"Unknown tag: {key}")
            assert(False)

    return ast_tree
 

# traverse the AST Tree and print it out
def traverse_and_print(tree: dict, indent: int):
    for _ in range(indent):
        print(" ", end="")
    if tree["type"] == Type.LEAF:
        print(f"{tree['nodeName']} ---> {tree['children'][0]}")
    else:
        print(f"{tree['nodeName']}")
        for child in tree["children"]:
            traverse_and_print(child, indent + 1)


# traverse the AST Tree and annotate the depth of every leaf
def traverse_and_annotate(tree: dict, depth: int):
    if "depth" in tree:
        print("Oops, the tree already has a 'depth' tag")
        assert(False)

    if tree["type"] == Type.LEAF:
        tree["depth"] = depth
    else:
        for child in tree["children"]:
            traverse_and_annotate(child, depth + 1)

# collect all the leaves in the AST Tree into the 'leaves_list'
def traverse_and_storeleaves(tree: dict, leaves_list: list):
    if tree["type"] == Type.LEAF:
        leaves_list.append(tree)
    else:
        for child in tree["children"]:
            traverse_and_storeleaves(child, leaves_list)

# printing out the whole path in the AST Tree
def bruteforce_search_path(leaves_list: list):
    result = []
    for i in range(len(leaves_list)):
        for j in range(i + 1, len(leaves_list)):
            result.append(get_the_path(leaves_list[i], leaves_list[j]))
    return result

# given two leaves, find the path between them
def get_the_path(oneLeave: dict, theOtherLeave: dict):
    result = ''
    result += str(oneLeave["children"][0]) + '↑'
    childright = theOtherLeave["children"][0]
    one_node_path = []
    theOther_node_path = []
    if oneLeave["depth"] > theOtherLeave["depth"]:
        diff = oneLeave["depth"] - theOtherLeave["depth"]
        for _ in range(diff):
            one_node_path.append(oneLeave["nodeName"])
            oneLeave = oneLeave["parent"]
    elif oneLeave["depth"] < theOtherLeave["depth"]:
        diff = theOtherLeave["depth"] - oneLeave["depth"]
        for _ in range(diff):
            theOther_node_path.insert(0, theOtherLeave["nodeName"])
            theOtherLeave = theOtherLeave["parent"]
   
    # FIX equal issue
    while oneLeave is not theOtherLeave:
        one_node_path.append(oneLeave["nodeName"])
        oneLeave = oneLeave["parent"]
        theOther_node_path.insert(0, theOtherLeave["nodeName"])
        theOtherLeave = theOtherLeave["parent"]
        if oneLeave is theOtherLeave:
            break
    
    one_node_path.append(oneLeave["nodeName"])

    for node in one_node_path:
        result += node + '↑'
    for node in theOther_node_path:
        result += node + '↓'
    result += str(childright)
    return result

def get_paths_on_tree(ast_json):
    # 导入 Json 文件 
    dict = json.loads(ast_json)
    # 构建 AST Tree
    ast_tree = {}
    ast_tree["type"], ast_tree["nodeName"], ast_tree["children"] = Type.ROOT, "CodeStart", []
    for code_line in dict:
        ast_tree["children"].append(buildAstTree(code_line, ast_tree))

    # 遍历 AST Tree, 标记所有 leaves 的深度
    traverse_and_annotate(ast_tree, 0)

    # 获取 AST Tree 的树叶集
    leaves_list = []
    traverse_and_storeleaves(ast_tree, leaves_list)

    # 根据 AST Tree 的树叶集搜索出所有路径
    paths = bruteforce_search_path(leaves_list)
    return paths

