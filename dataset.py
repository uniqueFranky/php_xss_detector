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
    
class ASTDataSet(torch.utils.data.Dataset):
    def __init__(self, data_path, prefix):
        vocab = preprocessing.build_ast_vocab()
        self.safe_paths = preprocessing.findAllFilesWithSpecifiedSuffix(data_path + '/safe', 'php')
        self.unsafe_paths = preprocessing.findAllFilesWithSpecifiedSuffix(data_path + '/unsafe', 'php')
        if os.path.isfile(prefix + 'left_features.json') and os.path.isfile(prefix + 'mid_features.json') \
            and os.path.isfile(prefix + 'right_features.json') and os.path.isfile(prefix + 'labels.json') \
            and os.path.isfile(prefix + 'left_positions.json') and os.path.isfile(prefix + 'right_positions.json'):
            with open(prefix + 'left_features.json', 'r') as f:
                self.left_features = json.loads(f.read())
            with open(prefix + 'mid_features.json', 'r') as f:
                self.mid_features = json.loads(f.read())
            with open(prefix + 'right_features.json', 'r') as f:
                self.right_features = json.loads(f.read())
            with open(prefix + 'labels.json', 'r') as f:
                self.labels = json.loads(f.read())
            with open(prefix + 'left_positions.json', 'r') as f:
                self.left_positions = json.loads(f.read())
            with open(prefix + 'right_positions.json', 'r') as f:
                self.right_positions = json.loads(f.read())
        else:
            self.left_features = []
            self.mid_features = []
            self.right_features = []
            self.labels = []
            self.left_positions = []
            self.right_positions = []

            safe_ast_paths = preprocessing.convert_file_paths_to_ast_paths(self.safe_paths)
            unsafe_ast_paths = preprocessing.convert_file_paths_to_ast_paths(self.unsafe_paths)

            for ast_paths in safe_ast_paths:
                left_nodes = []
                mid_paths = []
                right_nodes = []
                left_positions = []
                right_positions = []
                for ast_path in ast_paths:
                    left, left_pos, mid, right, right_pos = preprocessing.convert_ast_path_to_terminals_and_positions_and_path(ast_path)
                    left = vocab[left] if left in vocab else vocab['<unk>']
                    mid = vocab[mid] if mid in vocab else vocab['<unk>']
                    right = vocab[right] if right in vocab else vocab['<unk>']
                    left_nodes.append(left)
                    mid_paths.append(mid)
                    right_nodes.append(right)
                    left_positions.append(int(left_pos))
                    right_positions.append(int(right_pos))

                    
                self.left_features.append(left_nodes)
                self.mid_features.append(mid_paths)
                self.right_features.append(right_nodes)
                self.labels.append(0)
                self.left_positions.append(left_positions)
                self.right_positions.append(right_positions)

            for ast_paths in unsafe_ast_paths:
                left_nodes = []
                mid_paths = []
                right_nodes = []
                left_positions = []
                right_positions = []
                for ast_path in ast_paths:
                    left, left_pos, mid, right, right_pos = preprocessing.convert_ast_path_to_terminals_and_positions_and_path(ast_path)
                    left = vocab[left] if left in vocab else vocab['<unk>']
                    mid = vocab[mid] if mid in vocab else vocab['<unk>']
                    right = vocab[right] if right in vocab else vocab['<unk>']
                    left_nodes.append(left)
                    mid_paths.append(mid)
                    right_nodes.append(right)
                    left_positions.append(int(left_pos))
                    right_positions.append(int(right_pos))

                    
                self.left_features.append(left_nodes)
                self.mid_features.append(mid_paths)
                self.right_features.append(right_nodes)
                self.labels.append(1)
                self.left_positions.append(left_positions)
                self.right_positions.append(right_positions)


            with open(prefix + 'left_features.json', 'w') as f:
                f.write(json.dumps(self.left_features))
            with open(prefix + 'mid_features.json', 'w') as f:
                f.write(json.dumps(self.mid_features))
            with open(prefix + 'right_features.json', 'w') as f:
                f.write(json.dumps(self.right_features))
            with open(prefix + 'labels.json', 'w') as f:
                f.write(json.dumps(self.labels))
            with open(prefix + 'left_positions.json', 'w') as f:
                f.write(json.dumps(self.left_positions))
            with open(prefix + 'right_positions.json', 'w') as f:
                f.write(json.dumps(self.right_positions))
            
        random.seed(19260817)
        idx = [i for i in range(len(self.labels))]
        random.shuffle(idx)
        left_tmp = self.left_features.copy()
        mid_tmp = self.mid_features.copy()
        right_tmp = self.right_features.copy()
        labels_tmp = self.labels.copy()
        left_pos_tmp = self.left_positions.copy()
        right_pos_tmp = self.right_positions.copy()
        for i in range(len(self.labels)):
            left_tmp[i] = self.left_features[idx[i]]
            mid_tmp[i] = self.mid_features[idx[i]]
            right_tmp[i] = self.right_features[idx[i]]
            labels_tmp[i] = self.labels[idx[i]]
            left_pos_tmp[i] = self.left_positions[idx[i]]
            right_pos_tmp[i] = self.right_positions[idx[i]]
        self.left_features = left_tmp
        self.mid_features = mid_tmp
        self.right_features = right_tmp
        self.labels = labels_tmp
        self.left_positions = left_pos_tmp
        self.right_positions = right_pos_tmp

    def __getitem__(self, idx):
        return self.left_features[idx], self.left_positions[idx], self.mid_features[idx], self.right_features[idx], self.right_positions[idx], self.labels[idx]
        
    def __len__(self):
        return len(self.left_features)


train_dataset = ASTDataSet('dataset/train_datas', 'ast_train_')
test_dataset = ASTDataSet('dataset/test_datas', 'ast_test_')