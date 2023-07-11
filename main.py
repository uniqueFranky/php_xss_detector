import preprocessing
import glob
import os
import subprocess

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



tokens = set()
safe_php_paths = findAllFilesWithSpecifiedSuffix('./safe', 'php')
cnt = 1
for path in safe_php_paths:
    if(0 == cnt % 100):
        print(f'building dictionary for the %d-th php file' % cnt)
    cnt += 1
    for token in preprocessing.tokenize(preprocessing.read_php_code_from_file(path)):
        tokens.add(token)

print(tokens)
print(len(tokens))
    