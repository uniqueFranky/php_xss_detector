from torch import nn
import torch
import dataset
import random
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
        # self.linear2 = nn.Linear(hidden_size * 2, hidden_size * 3).to(device)
        # self.linear3 = nn.Linear(hidden_size * 3, hidden_size * 2).to(device)
        # self.linear4 = nn.Linear(hidden_size * 2, output_size).to(device)
        torch.nn.init.xavier_uniform(self.linear1.weight)
        torch.nn.init.xavier_uniform(self.embedding.weight)




    def forward(self, x):
        x = self.embedding(x)
        x, _ = self.rnn(x)
        x = x[:, -1, :]
        x = self.linear1(x)
        # x = torch.relu(x)
        # x = self.linear2(x)
        # x = torch.relu(x)
        # x = self.linear3(x)
        # x = torch.relu(x)
        # x = self.linear4(x)
        x = torch.tanh(x)
        return x
        

def train(vocab_size, embedding_size, hidden_size, num_layers, output_size, num_epoch, lr):
    model = Model(vocab_size, embedding_size, hidden_size, num_layers, output_size).to(device)
    criterion = nn.CrossEntropyLoss().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    datas = dataset.CodeDataSet()
    train_datas = []
    test_datas = []
    for i in range(int(0.9 * len(datas))):
        train_datas.append(datas[i])
    for i in range(int(0.9 * len(datas) + 1), len(datas)):
        test_datas.append(datas[i])
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

        torch.save(model.state_dict(), 'checkpoint#' + epoch + '.ckp')
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
            print('accuracy rate =', acc / len(test_datas))
        

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