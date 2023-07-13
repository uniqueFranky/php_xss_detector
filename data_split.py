import preprocessing
import os
import random

def split_datas():
    safe_paths = preprocessing.findAllFilesWithSpecifiedSuffix('./safe', 'php')
    random.shuffle(safe_paths)
    for i in range(int(len(safe_paths) / 10)):
        path = safe_paths[i]
        os.system('mv ' + path + ' ./dataset/test_datas/safe')
    
    unsafe_paths = preprocessing.findAllFilesWithSpecifiedSuffix('./safe', 'php')
    random.shuffle(unsafe_paths)
    for i in range(int(len(unsafe_paths) / 10)):
        path = unsafe_paths[i]
        os.system('mv ' + path + ' ./dataset/test_datas/unsafe')

split_datas()