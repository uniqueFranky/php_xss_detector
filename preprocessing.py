import jk_php_tokenizer
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
    

def build_dict(tokens: list[str]) -> dict:
    result = {}
    tokens = list(set(tokens))
    tokens.sort()
    for token in tokens:
        result.update({token: len(result)})
    return result