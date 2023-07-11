from torch import nn
import torch
import dataset
import numpy
import preprocessing

class Model(nn.Module):
    def __init__(self, vocab_size, embedding_size, hidden_size, num_layers, output_size):
        super().__init__()
        vocab = preprocessing.build_dict()
        self.embedding = nn.Embedding(num_embeddings=vocab_size, embedding_dim=embedding_size, padding_idx=vocab['<pad>'])
        self.rnn = nn.RNN(input_size=embedding_size, hidden_size=hidden_size, num_layers=num_layers, batch_first=True)
        self.linear = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = self.embedding(x)
        x = torch.relu(x)
        x, _ = self.rnn(x)
        x = x[:, -1, :]
        x = self.linear(x)
        x = torch.sigmoid(x)
        return x
        

def train(vocab_size, embedding_size, hidden_size, num_layers, output_size, num_epoch, lr):
    model = Model(vocab_size, embedding_size, hidden_size, num_layers, output_size)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=lr)
    datas = dataset.CodeDataSet()
    loader = torch.utils.data.DataLoader(datas, batch_size=64, shuffle=True)

    for epoch in range(num_epoch):
        for x, y in loader:
            pred = model(x)
            loss = criterion(pred, y)
            loss.backward()
            print(loss.item())
            optimizer.step()
            optimizer.zero_grad()