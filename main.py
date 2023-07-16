import model
import subprocess
import preprocessing
import json
import dataset

# model.train(vocab_size=168, embedding_size=80, hidden_size=80, num_layers=8, output_size=2, num_epoch=5000, lr=0.00001)
# train_dataset = dataset.ASTDataSet('./dataset/train_datas', prefix='ast_train_')
# left, mid, right, label = train_dataset[0]

model.ast_train(vocab_size=2076, embedding_size=500, hidden_size=500, output_size=2, num_epoch=200, lr=0.0001)
