import torch
import preprocessing
import os
import json
import random
class CodeDataSet(torch.utils.data.Dataset):
    def __init__(self, data_path, prefix):
        self.safe_paths = preprocessing.findAllFilesWithSpecifiedSuffix(data_path + '/safe', 'php')
        self.unsafe_paths = preprocessing.findAllFilesWithSpecifiedSuffix(data_path + '/unsafe', 'php')
        if os.path.isfile(prefix + 'features.json') and os.path.isfile(prefix + 'labels.json'):
            with open(prefix + 'features.json', 'r') as f:
                self.features = json.loads(f.read())
            with open(prefix + 'labels.json', 'r') as f:
                self.labels = json.loads(f.read())
        else:
            self.features = []
            self.labels = []
            vocab = preprocessing.build_dict()
            for path in self.safe_paths:
                tokens = preprocessing.tokenize(preprocessing.read_php_code_from_file(path))
                for i, _ in enumerate(tokens):
                    tokens[i] = vocab[tokens[i]] if tokens[i] in vocab else vocab['<unk>']
                self.features.append(tokens)
                self.labels.append(0)
            for path in self.unsafe_paths:
                tokens = preprocessing.tokenize(preprocessing.read_php_code_from_file(path))
                for i, _ in enumerate(tokens):
                    tokens[i] = vocab[tokens[i]] if tokens[i] in vocab else vocab['<unk>']
                self.features.append(tokens)
                self.labels.append(1)
            with open(prefix + 'features.json', 'w') as f:
                f.write(json.dumps(self.features))
            with open(prefix + 'labels.json', 'w') as f:
                f.write(json.dumps(self.labels))
        random.seed(19260817)
        tmp = list(zip(self.features, self.labels))
        random.shuffle(tmp)
        self.features, self.labels = zip(*tmp)
        self.features, self.labels = list(self.features), list(self.labels)

    def __len__(self):
        return len(self.safe_paths) + len(self.unsafe_paths)
    
    def __getitem__(self, idx):
        return (self.features[idx], self.labels[idx])