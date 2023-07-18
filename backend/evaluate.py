import subprocess
import sys
import torch
import math
sys.path.append("..")
import draw
import preprocessing
from model import ASTModel


def get_ast_graph(code, path_to_save, ast_path_to_red):
    parser = subprocess.run(['php', '../parser.php', code], check=True, stdout=subprocess.PIPE)
    ast_json = parser.stdout.decode()
    graph = draw.build_graph_by_json(ast_json)
    graph.find_specific_path_on_graph(ast_path_to_red)
    graph.render(path_to_save)

def get_code_paths(model_path, code):
    model = ASTModel(vocab_size=2676, embedding_size=500, hidden_size=500, output_size=2)
    model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
    model.eval()
    ast_vocab = preprocessing.build_ast_vocab()
    paths = preprocessing.convert_code_to_ast_paths(code)
    left_nodes = []
    mid_paths = []
    right_nodes = []
    for ast_path in paths:
        left, mid, right = preprocessing.convert_ast_path_to_terminals_and_path(ast_path)
        left = ast_vocab[left] if left in ast_vocab else ast_vocab['<unk>']
        mid = ast_vocab[mid] if mid in ast_vocab else ast_vocab['<unk>']
        right = ast_vocab[right] if right in ast_vocab else ast_vocab['<unk>']
        left_nodes.append(left)
        mid_paths.append(mid)
        right_nodes.append(right)

    left = torch.IntTensor(left_nodes)
    mid = torch.IntTensor(mid_paths)
    right = torch.IntTensor(right_nodes)

    pred = model(left, mid, right)
    left = model.embedding(left)
    mid = model.embedding(mid)
    right = model.embedding(right)
    x = torch.cat((left, mid, right), dim=1)
    x = model.combine(x)
    x = torch.relu(x)
    alpha = torch.matmul(x, model.attention)
    # alpha = torch.tanh(alpha)
    alpha = alpha.squeeze(1)
    sorted, idx = torch.topk(alpha, 20)
    return sorted[rank].item(), paths[idx[rank]], pred


args = sys.argv
code = args[1]
rank = int(args[2]) - 1
file_name = args[3]

attn, path, pred = get_code_paths('model2_96.ckp', code)
print(attn)
print(path)
neg = pred[0].item()
pos = pred[1].item()
print(math.exp(neg) / (math.exp(pos) + math.exp(neg)))
print(math.exp(pos) / (math.exp(pos) + math.exp(neg)))

get_ast_graph(code, file_name, path)

