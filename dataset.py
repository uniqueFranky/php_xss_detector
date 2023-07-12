import torch
import preprocessing
import os
import json
import random
class CodeDataSet(torch.utils.data.Dataset):
    def __init__(self):
        self.safe_paths = preprocessing.findAllFilesWithSpecifiedSuffix('./safe', 'php')
        self.unsafe_paths = preprocessing.findAllFilesWithSpecifiedSuffix('./unsafe', 'php')
        if os.path.isfile('features.json') and os.path.isfile('labels.json'):
            with open('features.json', 'r') as f:
                self.features = json.loads(f.read())
            with open('labels.json', 'r') as f:
                self.labels = json.loads(f.read())
        else:
            self.features = []
            self.labels = []
            vocab = preprocessing.build_dict()
            for path in self.safe_paths:
                tokens = preprocessing.tokenize(preprocessing.read_php_code_from_file(path))
                for i, _ in enumerate(tokens):
                    tokens[i] = vocab[tokens[i]]
                self.features.append(tokens)
                self.labels.append(0)
            for path in self.unsafe_paths:
                tokens = preprocessing.tokenize(preprocessing.read_php_code_from_file(path))
                for i, _ in enumerate(tokens):
                    tokens[i] = vocab[tokens[i]]
                self.features.append(tokens)
                self.labels.append(1)
            with open('features.json', 'w') as f:
                f.write(json.dumps(self.features))
            with open('labels.json', 'w') as f:
                f.write(json.dumps(self.labels))
        random.seed(19260817)
        tmp = list(zip(self.features, self.labels))
        random.shuffle(tmp)
        self.features, self.labels = zip(*tmp)
        self.features, self.labels = list(self.features), list(self.labels)

    def __len__(self):
        return len(self.safe_paths) + len(self.unsafe_paths)
    
    def __getitem__(self, idx):
        return (torch.IntTensor(self.features[idx]), self.labels[idx])