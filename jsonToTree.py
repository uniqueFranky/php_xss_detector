import os
import json


node_unused = ["Stmt_InlineHTML"]
skip_tag = ["attributes", "nodeType"]
leaf_list = ["value", "name", "parts"]

# Load the json file into a dictionary and return it
def loadJson(filepath):
    with open(filepath, 'r') as f:
        code = json.load(f)
    return code


# check if elem is a leaf value
def checkLeaf(elem):
    if type(elem) == dict:
        return False
    if type(elem) == str and elem == 'null':
        return False
    if type(elem) == list and elem == []:
        return False
    return True


# check if all the elements in the list is the same type 
def checkListType(elemList):
    if len(elemList) != 0:
        t = type(elemList[0])
        for elem in elemList:
            if type(elem) != t:
                print(elemList)
                assert(False)


# given the json data(stored in dictionary), build the AST
def buildAstTree(dict_tree: dict, parent: dict): 

    # dict_tree is a unused node
    if dict_tree['nodeType'] in node_unused:
        return None

    # dict_tree is a leaf node
    for leaf_elem in leaf_list:
        if leaf_elem in dict_tree and checkLeaf(dict_tree[leaf_elem]) == True:
            return {'isLeaf': True, 'nodeType': dict_tree['nodeType'], 'value': dict_tree[leaf_elem], 'parent': parent, \
                    'line': dict_tree["attributes"]["startLine"]}

    # dict_tree is a mid node
    ret_tree = {}
    ret_tree['isLeaf'] = False
    ret_tree['nodeType'] = dict_tree["nodeType"]
    ret_tree['children'] = []
    ret_tree['parent'] = parent
    for tag, value in dict_tree.items():
        if tag in skip_tag:
            continue
        if type(value) == dict:
            child = buildAstTree(value, ret_tree)
            if child:
                ret_tree["children"].append(child)
        if type(value) == list:
            checkListType(value)
            for elem in value:
                child = buildAstTree(elem, ret_tree)
                if child:
                    ret_tree["children"].append(child)

    # dict_tree has no children
    if len(ret_tree["children"]) == 0:
        return None

    return ret_tree
 

# traverse the AST Tree and print it out
def traverse_and_print(tree: dict, indent: int, fp):
    for _ in range(indent):
        fp.write(" ")
    if tree["isLeaf"] == True:
        fp.write(f"{tree['nodeType']} ---> {tree['value']}\n")
    else:
        fp.write(f"{tree['nodeType']}\n")
        for child in tree["children"]:
            traverse_and_print(child, indent + 1, fp)


# traverse the AST Tree and annotate the depth of every leaf
def traverse_and_annotate(tree: dict, depth: int):
    if "depth" in tree:
        print("Oops, the tree already has a 'depth' tag")
        assert(False)

    if tree["isLeaf"] == True:
        tree["depth"] = depth
    else:
        for child in tree["children"]:
            traverse_and_annotate(child, depth + 1)


# collect all the leaves in the AST Tree into the 'leaves_list'
def traverse_and_storeleaves(tree: dict, leaves_list: list):
    if tree["isLeaf"] == True:
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
    childleft = oneLeave
    childright = theOtherLeave
    one_node_path = []
    theOther_node_path = []
    result = ''

    if oneLeave["depth"] > theOtherLeave["depth"]:
        diff = oneLeave["depth"] - theOtherLeave["depth"]
        for _ in range(diff):
            one_node_path.append(oneLeave["nodeType"])
            oneLeave = oneLeave["parent"]
    elif oneLeave["depth"] < theOtherLeave["depth"]:
        diff = theOtherLeave["depth"] - oneLeave["depth"]
        for _ in range(diff):
            theOther_node_path.insert(0, theOtherLeave["nodeType"])
            theOtherLeave = theOtherLeave["parent"]
   
    while oneLeave is not theOtherLeave:
        one_node_path.append(oneLeave["nodeType"])
        oneLeave = oneLeave["parent"]
        theOther_node_path.insert(0, theOtherLeave["nodeType"])
        theOtherLeave = theOtherLeave["parent"]
        if oneLeave is theOtherLeave:
            break
    
    theOther_node_path.insert(0, oneLeave["nodeType"])
    result += '(' + str(childleft['value']) + ',' + str(childleft['line']) + ')' + '↑'
    for node in one_node_path:
        result += node + '↑'
    for node in theOther_node_path:
        result += node + '↓'
    result += '(' + str(childright['value']) + ',' + str(childright['line']) + ')'
    return result


def get_paths_on_tree(ast_json):
    # 导入 Json 文件 
    dict = json.loads(ast_json)
    # 构建 AST Tree
    ast_tree = {}
    ast_tree["isLeaf"], ast_tree["nodeType"], ast_tree["children"] = False, "CodeStart", []
    for code_line in dict:
        child = buildAstTree(code_line, ast_tree)
        if child:
            ast_tree["children"].append(child)

    # 遍历 AST Tree, 标记所有 leaves 的深度
    traverse_and_annotate(ast_tree, 0)

    # traverse_and_print(ast_tree, 0, fp)

    # 获取 AST Tree 的树叶集
    leaves_list = []
    traverse_and_storeleaves(ast_tree, leaves_list)

    # 根据 AST Tree 的树叶集搜索出所有路径
    return bruteforce_search_path(leaves_list)
    # return paths



        
