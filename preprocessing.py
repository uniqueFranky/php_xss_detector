import jk_php_tokenizer
import os
import subprocess
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
        if '\n' != token and ' ' != token:
            result.append(token.strip())
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
    tokens = set()
    safe_php_paths = findAllFilesWithSpecifiedSuffix('./safe', 'php')
    cnt = 1
    for path in safe_php_paths:
        if(0 == cnt % 100):
            print(f'building dictionary for the %d-th php file' % cnt)
        cnt += 1
        for token in tokenize(read_php_code_from_file(path)):
            tokens.add(token)

    unsafe_php_paths = findAllFilesWithSpecifiedSuffix('./unsafe', 'php')
    cnt = 1
    for path in safe_php_paths:
        if(0 == cnt % 100):
            print(f'building dictionary for the %d-th php file' % cnt)
        cnt += 1
        for token in tokenize(read_php_code_from_file(path)):
            tokens.add(token)
    for token in tokens:
        result.update({token: len(result)})
    return result