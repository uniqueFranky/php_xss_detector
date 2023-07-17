import os
import subprocess
import json
import jsonToTree
def read_php_code_from_file(file_path: str) -> str:
    result = ''
    with open(file_path, 'r') as f:
        in_php = False
        for line in f.readlines():
            li = line.strip()

            if False == in_php and False == li.startswith('<?php'): # omit inner HTML
                continue
            elif True == li.startswith('<?php'):
                in_php = True
                result += li + '\n'
            elif True == in_php and False == li.startswith('//'):
                if '' != li:
                    result += li + '\n'
                if True == li.endswith('?>'):
                    in_php = False

    return result

def tokenize(code: str) -> list:
    returned = subprocess.run(['php', 'tokenizer.php', code], check=True, stdout=subprocess.PIPE)
    returned = returned.stdout.decode()
    tokens = returned.split(',')
    result = []
    for token in tokens:
        if '\n' != token and ' ' != token and '' != token.strip():
            result.append(str(token.strip()))
    return result
    
def findAllFilesWithSpecifiedSuffix(target_dir, target_suffix="php"):
    find_res = []
    target_suffix_dot = "." + target_suffix
    walk_generator = os.walk(target_dir)
    for root_path, dirs, files in walk_generator:
        if len(files) < 1:
            continue
        for file in files:
            file_name, suffix_name = os.path.splitext(file)
            if suffix_name == target_suffix_dot:
                find_res.append(os.path.join(root_path, file))
    return find_res

def build_dict() -> dict:
    result = {}
    if os.path.isfile('dict.json'):
        with open('dict.json', 'r') as f:
            result = json.loads(f.read())
        return result
    tokens = set()
    safe_php_paths = findAllFilesWithSpecifiedSuffix('./dataset/train_datas/safe', 'php')
    cnt = 1
    for path in safe_php_paths:
        if(0 == cnt % 100):
            print(f'building dictionary for the %d-th php file' % cnt)
        cnt += 1
        for token in tokenize(read_php_code_from_file(path)):
            tokens.add(token)

    unsafe_php_paths = findAllFilesWithSpecifiedSuffix('./dataset/train_datas/unsafe', 'php')
    cnt = 1
    for path in unsafe_php_paths:
        if(0 == cnt % 100):
            print(f'building dictionary for the %d-th php file' % cnt)
        cnt += 1
        for token in tokenize(read_php_code_from_file(path)):
            tokens.add(token)
    for token in tokens:
        result.update({token: len(result)})
    result.update({'<pad>': len(result)})
    result.update({'<unk>': len(result)})
    json_str = json.dumps(result)
    with open('dict.json', 'w') as f:
        f.write(json_str)
    return result

def convert_code_to_ast_paths(code: str):
    parser = subprocess.run(['php', 'parser.php', code], check=True, stdout=subprocess.PIPE)
    ast_json = parser.stdout.decode()
    paths = jsonToTree.get_paths_on_tree(ast_json)
    return paths

def convert_file_paths_to_ast_paths(file_paths):
    result = []
    for file_path in file_paths:
        with open(file_path, 'r') as f:
            code = f.read()
            ast_path = convert_code_to_ast_paths(code)
            result.append(ast_path)
    return result

def convert_whole_dataset_to_ast_paths(train_path='./dataset/train_datas/', test_path='./dataset/test_datas/'):
    train_safe_file_paths = findAllFilesWithSpecifiedSuffix(train_path + 'safe/', 'php')
    train_unsafe_file_paths = findAllFilesWithSpecifiedSuffix(train_path + 'unsafe/', 'php')
    train_safe_ast_paths = convert_file_paths_to_ast_paths(train_safe_file_paths)
    train_unsafe_ast_paths = convert_file_paths_to_ast_paths(train_unsafe_file_paths)

    test_safe_file_paths = findAllFilesWithSpecifiedSuffix(test_path + 'safe/', 'php')
    test_unsafe_file_paths = findAllFilesWithSpecifiedSuffix(test_path + 'unsafe/', 'php')
    test_safe_ast_paths = convert_file_paths_to_ast_paths(test_safe_file_paths)
    test_unsafe_ast_paths = convert_file_paths_to_ast_paths(test_unsafe_file_paths)

    return train_safe_ast_paths, train_unsafe_ast_paths, test_safe_ast_paths, test_unsafe_ast_paths

def convert_ast_path_to_terminals_and_positions_and_path(ast_path: str):
    st = ast_path.find('↑')
    ed = ast_path.rfind('↓')
    left_node = ast_path[1: st - 1]
    right_node = ast_path[ed + 2: -1]
    mid_path = ast_path[st + 1: ed]
    st = left_node.rfind(',')
    left_pos = left_node[st + 1: ]
    left_node = left_node[: st]
    st = right_node.rfind(',')
    right_pos = right_node[st + 1: ]
    right_node = right_node[: st]
    return left_node, left_pos, mid_path, right_node, right_pos

def build_ast_vocab(train_path='./dataset/train_datas/', test_path='./dataset/test_datas/') -> dict:
    if os.path.isfile('ast_dict.json'):
        with open('ast_dict.json', 'r') as f:
            vocab = json.loads(f.read())
        return vocab
    
    train_safe_ast_paths, train_unsafe_ast_paths, test_safe_ast_paths, test_unsafe_ast_paths = \
        convert_whole_dataset_to_ast_paths(train_path, test_path)
    
    tokens = set()
    for ast_paths in train_safe_ast_paths:
        for ast_path in ast_paths:
            left_node, _, mid_path, right_node, _ = convert_ast_path_to_terminals_and_positions_and_path(ast_path)
            tokens.add(left_node)
            tokens.add(right_node)
            tokens.add(mid_path)
    for ast_paths in train_unsafe_ast_paths:
        for ast_path in ast_paths:
            left_node, _, mid_path, right_node, _ = convert_ast_path_to_terminals_and_positions_and_path(ast_path)
            tokens.add(left_node)
            tokens.add(right_node)
            tokens.add(mid_path)

    vocab = {}
    for token in tokens:
        vocab.update({token: len(vocab)})
    vocab.update({'<pad>': len(vocab)})
    vocab.update({'<unk>': len(vocab)})

    with open('ast_dict.json', 'w') as f:
        vocab_json = json.dumps(vocab)
        f.write(vocab_json)

    return vocab


build_ast_vocab()

