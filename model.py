from torch import nn
import torch
import dataset
import random
import preprocessing

device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
print('running on ', device)
device = torch.device(device)

class Model(nn.Module):
    def __init__(self, vocab_size, embedding_size, hidden_size, num_layers, output_size):
        super().__init__()
        vocab = preprocessing.build_dict()
        self.num_layers = num_layers
        self.hidden_size = hidden_size
        self.embedding = nn.Embedding(num_embeddings=vocab_size, embedding_dim=embedding_size, padding_idx=vocab['<pad>']).to(device)
        self.rnn = nn.RNN(input_size=embedding_size, hidden_size=hidden_size, num_layers=num_layers, batch_first=True).to(device)
        self.linear1 = nn.Linear(hidden_size, hidden_size * 2).to(device)
        self.linear2 = nn.Linear(hidden_size * 2, hidden_size * 3).to(device)
        self.linear3 = nn.Linear(hidden_size * 3, hidden_size).to(device)
        self.linear4 = nn.Linear(hidden_size, output_size).to(device)

    def forward(self, x):
        x = self.embedding(x)
        x, _ = self.rnn(x)
        x = x[-1:, :]
        x = self.linear1(x)
        x = torch.tanh(x)
        x = self.linear2(x)
        x = torch.relu(x)
        x = self.linear3(x)
        x = torch.tanh(x)
        x = self.linear4(x)
        x = torch.tanh(x)
        return x
        

def train(vocab_size, embedding_size, hidden_size, num_layers, output_size, num_epoch, lr):
    model = Model(vocab_size, embedding_size, hidden_size, num_layers, output_size).to(device)
    criterion = nn.CrossEntropyLoss().to(device)
    optimizer = torch.optim.SGD(model.parameters(), lr=lr)
    datas = dataset.CodeDataSet()
    
    for epoch in range(num_epoch):
        acc = 0
        for x, y in datas:
            x = x.to(device)
            pred = model(x)
            ty = torch.LongTensor([y]).to(device)
            loss = criterion(pred, ty)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        print(f'epoch =  %d, acc = %f' % (epoch + 1, acc / len(datas)))
        torch.save(model.state_dict(), 'checkpoint.ckp')
        print(f'checkpoint %d / %d written' %(epoch + 1, num_epoch))
        with torch.no_grad():
            acc = 0
            for x, y in datas:
                x = x.to(device)
                pred = model(x)
                if pred[0][0].item() > pred[0][1].item() and 0 == y:
                    acc += 1
                if pred[0][1].item() > pred[0][0].item() and 1 == y:
                    acc += 1
            print(f'accuracy rate = %f' % acc / len(datas))
        
