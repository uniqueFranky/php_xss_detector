from torch import nn
import torch
import dataset
import os
import preprocessing

device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
print('running on ', device)
device = torch.device(device)
vocab = preprocessing.build_dict()

class Model(nn.Module):
    def __init__(self, vocab_size, embedding_size, hidden_size, num_layers, output_size):
        super().__init__()
        self.num_layers = num_layers
        self.hidden_size = hidden_size
        self.embedding = nn.Embedding(num_embeddings=vocab_size, embedding_dim=embedding_size, padding_idx=vocab['<pad>']).to(device)
        self.rnn = nn.LSTM(input_size=embedding_size, hidden_size=hidden_size, num_layers=num_layers, batch_first=True).to(device)
        self.linear1 = nn.Linear(hidden_size, output_size).to(device)
        torch.nn.init.xavier_uniform_(self.linear1.weight)
        torch.nn.init.xavier_uniform_(self.embedding.weight)

    def forward(self, x):
        x = self.embedding(x)
        x, _ = self.rnn(x)
        x = x[:, -1, :]
        x = self.linear1(x)
        x = torch.tanh(x)
        return x
        

def train(vocab_size, embedding_size, hidden_size, num_layers, output_size, num_epoch, lr):
    os.system('rm result.txt')
    model = Model(vocab_size, embedding_size, hidden_size, num_layers, output_size).to(device)
    criterion = nn.CrossEntropyLoss().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    train_datas = dataset.CodeDataSet('./dataset/train_datas', prefix='train_')
    test_datas = dataset.CodeDataSet('./dataset/test_datas', prefix='test_')
    loader = torch.utils.data.DataLoader(train_datas, batch_size=16, collate_fn=collate_fn)
    for epoch in range(num_epoch):
        for x, y in loader:
            x = x.to(device)
            y = y.to(device)
            pred = model(x)
            loss = criterion(pred, y)
            optimizer.zero_grad()
            loss.backward()
            # with open('grad.txt', 'a') as f:
                # f.write(str(model.linear1.weight.grad))
            optimizer.step()

        torch.save(model.state_dict(), 'checkpoint#' + str(epoch) + '.ckp')
        print(f'checkpoint %d / %d written' %(epoch + 1, num_epoch))
        with torch.no_grad():
            acc = 0
            for x, y in test_datas:
                x = torch.IntTensor(x).to(device)
                x = x.unsqueeze(0)
                pred = model(x)
                if pred[0][0].item() > pred[0][1].item() and 0 == y:
                    acc += 1
                if pred[0][1].item() > pred[0][0].item() and 1 == y:
                    acc += 1
            with open('result.txt', 'a') as f:
                f.write('on test datas: accuracy rate = ' + str(acc / len(test_datas)) + '\n')
        with torch.no_grad():
            acc = 0
            for x, y in train_datas:
                x = torch.IntTensor(x).to(device)
                x = x.unsqueeze(0)
                pred = model(x)
                if pred[0][0].item() > pred[0][1].item() and 0 == y:
                    acc += 1
                if pred[0][1].item() > pred[0][0].item() and 1 == y:
                    acc += 1
            with open('result.txt', 'a') as f:
                f.write('on train datas: accuracy rate = ' + str(acc / len(train_datas)) + '\n')
        

def collate_fn(batch):
    max_length = 0
    for row in batch:
        max_length = max(max_length, len(row[0]))
    features = []
    labels = []
    for row in batch:
        features.append(row[0])
        while len(features[-1]) < max_length:
            features[-1].append(vocab['<pad>'])
        labels.append(row[1])
    return torch.IntTensor(features), torch.LongTensor(labels)

ast_vocab = preprocessing.build_ast_vocab()
class ASTModel(nn.Module):
    def __init__(self, vocab_size, embedding_size, hidden_size, output_size):
        super().__init__()
        self.embedding_size = embedding_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.embedding = nn.Embedding(vocab_size, embedding_size, padding_idx=ast_vocab['<pad>']).to(device)
        self.combine = nn.Linear(3 * embedding_size, hidden_size).to(device)
        self.attention = torch.rand(hidden_size, 1).to(device)
        self.linear = nn.Linear(hidden_size, output_size).to(device)
        torch.nn.init.xavier_uniform_(self.linear.weight)
        torch.nn.init.xavier_uniform_(self.combine.weight)
        torch.nn.init.xavier_uniform_(self.embedding.weight)

    def forward(self, left, mid, right):
        left = self.embedding(left)
        mid = self.embedding(mid)
        right = self.embedding(right)
        x = torch.cat((left, mid, right), dim=1).to(device)
        x = self.combine(x)
        x = torch.relu(x)
        alpha = torch.matmul(x, self.attention).to(device)
        alpha = torch.tanh(alpha)
        x = torch.mul(x, alpha)
        x = torch.sum(x, dim=0)
        x = self.linear(x)
        x = torch.tanh(x)
        return x


def ast_train(vocab_size, embedding_size, hidden_size, output_size, num_epoch, lr):
    model = ASTModel(vocab_size, embedding_size, hidden_size, output_size).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss().to(device)
    train_dataset = dataset.ASTDataSet('./dataset/train_datas', prefix='ast_train_')
    test_dataset = dataset.ASTDataSet('./dataset/test_datas', prefix='ast_test_')
    print(len(train_dataset))
    print(len(test_dataset))
    for epoch in range(num_epoch):
        print('epoch =', epoch + 1)
        for left, mid, right, label in train_dataset:
            left = torch.tensor(left).to(device)
            mid = torch.tensor(mid).to(device)
            right = torch.tensor(right).to(device)
            label = torch.tensor(label).to(device)
            pred = model(left, mid, right).to(device)
            loss = criterion(pred, label)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        acc = 0
        for left, mid, right, label in train_dataset:
            with torch.no_grad():
                left = torch.tensor(left).to(device)
                mid = torch.tensor(mid).to(device)
                right = torch.tensor(right).to(device)
                label = torch.tensor(label).to(device)
                pred = model(left, mid, right).to(device)
                if pred[0].item() > pred[1].item() and 0 == label.item():
                    acc += 1
                if pred[1].item() > pred[0].item() and 1 == label.item():
                    acc += 1
        print('on train dataset: acc =', acc / len(train_dataset))

        acc = 0
        for left, mid, right, label in test_dataset:
            with torch.no_grad():
                left = torch.tensor(left).to(device)
                mid = torch.tensor(mid).to(device)
                right = torch.tensor(right).to(device)
                label = torch.tensor(label).to(device)
                pred = model(left, mid, right).to(device)
                if pred[0].item() > pred[1].item() and 0 == label.item():
                    acc += 1
                if pred[1].item() > pred[0].item() and 1 == label.item():
                    acc += 1
        print('on test dataset: acc =', acc / len(test_dataset))

