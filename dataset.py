import torch
import preprocessing
class CodeDataSet(torch.utils.data.Dataset):
    def __init__(self):
        self.safe_paths = preprocessing.findAllFilesWithSpecifiedSuffix('./safe', 'php')
        self.unsafe_paths = preprocessing.findAllFilesWithSpecifiedSuffix('./unsafe', 'php')

    def __len__(self):
        return len(self.safe_paths) + len(self.unsafe_paths)
    
    def __getitem__(self, idx):
        if idx < len(self.safe_paths):
            path = self.safe_paths[idx]
            label = 0
        else:
            path = self.unsafe_paths[idx - len(self.safe_paths)]
            label = 1
        tokens = preprocessing.tokenize(preprocessing.read_php_code_from_file(path))
        vocab = preprocessing.build_dict()
        for i, _ in enumerate(tokens):
            assert(tokens[i] in vocab)
            tokens[i] = vocab[tokens[i]]
        while(len(tokens) < 150):
            tokens.append(vocab['<pad>'])
        return (torch.IntTensor(tokens), label)