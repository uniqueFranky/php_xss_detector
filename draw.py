import graphviz
import jsonToTree
import json
import subprocess

class ASTGraph:
    def __init__(self, dot) -> None:
        self.graph = dot
        self.edges = []
        self.edges_of_labels = []
        self.vocab = {}
        self.cnt = 0
        self.destinations_for = {}
        self.sources_for = {}
        self.found = False
        self.paths = []
    
    def node(self, label: str):
        self.cnt += 1
        self.graph.node(str(self.cnt), label)
        self.vocab.update({self.cnt: label})

    def edge(self, st: int, ed: int):
        self.graph.edge(str(st), str(ed), color='black')
        self.edges.append((st, ed))
        self.edges_of_labels.append((self.vocab[st], self.vocab[ed]))
        if st in self.destinations_for:
            self.destinations_for[st].append(ed)
        else:
            self.destinations_for.update({st: [ed]})
        if ed in self.sources_for:
            self.sources_for[ed].append(st)
        else:
            self.sources_for.update({ed: [st]})

    def render(self, path: str):
        self.graph.render(path)

    def get_cnt(self):
        return self.cnt
    
    def get_edges(self):
        return self.edges
    
    def get_edges_of_labels(self):
        return self.edges_of_labels
    
    def get_destinations(self):
        return self.destinations_for
    
    def get_sources(self):
        return self.sources_for
    
    def get_edge(self, st: int, ed: int):
        for i, statement in enumerate(self.graph.body):
            if '->' in statement:  # 检查是否为边的语句
                parts = statement.split('->')
                tail = parts[0].strip()  # 源节点
                head = parts[1].strip().split()[0]  # 目标节点

                if tail == str(st) and head == str(ed):
                    self.graph.body[i] = statement.replace('[color=black]', '[color=red]')
                    break
    
    def dfs(self, x: int, path_to_find: str, up: bool):
        up_pos = path_to_find.find('↑')
        down_pos = path_to_find.find('↓')
        
        up_pos = up_pos if up_pos > 0 else 100000000
        down_pos = down_pos if down_pos > 0 else 100000000

        if 100000000 == up_pos and 100000000 == down_pos:
            label = path_to_find
        else:
            label = path_to_find[: min(down_pos, up_pos)]

        pts = self.sources_for[x] if up else self.destinations_for[x]

        for v in pts:
            if self.found:
                    return
            if self.vocab[v] == label:
                if up:
                    self.paths.append((v, x))
                else:
                    self.paths.append((x, v))
                if label == path_to_find:
                    self.found = True
                    return
                self.dfs(v, path_to_find[min(down_pos, up_pos) + 1: ], (up_pos < down_pos))
                if self.found:
                    return
                self.paths = self.paths[: -1]

    
    def find_specific_path_on_graph(self, path_to_find: str):
        up_pos = path_to_find.find('↑')
        label = path_to_find[: up_pos]
        self.found = False
        self.paths = []
        for i in range(1, self.get_cnt() + 1):
            if self.vocab[i] == label:
                self.dfs(i, path_to_find[up_pos + 1: ], True)
                if self.found:
                    break
        for st, ed in self.paths:
            self.get_edge(st, ed)
        


def build_graph(tree, graph):
    graph.node(tree['nodeType'])
    self_id = graph.get_cnt()
    if tree['isLeaf']:
        graph.node(str(tree['value']))
        child_id = graph.get_cnt()
        graph.edge(self_id, child_id)
    else:
        for child in tree["children"]:
            child_id = build_graph(child, graph)
            graph.edge(self_id, child_id)
    return self_id

def build_graph_by_json(ast_json):
    dict = json.loads(ast_json)
    ast_tree = {}
    ast_tree["isLeaf"], ast_tree["nodeType"], ast_tree["children"] = False, "CodeStart", []
    for code_line in dict:
        child = jsonToTree.buildAstTree(code_line, ast_tree)
        if child:
            ast_tree["children"].append(child)
    graph = ASTGraph(graphviz.Digraph('AST'))
    graph.node('CodeStart')
    for child in ast_tree['children']:
        child_id = build_graph(child, graph)
        graph.edge(1, child_id)

    return graph

with open('dataset/test_datas/safe/CWE_79__system__CAST-func_settype_int__Use_untrusted_data_script-quoted_Event_Handler.php', 'r') as f:
    code = f.read()
    parser = subprocess.run(['php', 'parser.php', code], check=True, stdout=subprocess.PIPE)
    ast_json = parser.stdout.decode()
    graph = build_graph_by_json(ast_json)
    
    path_to_find = 'tainted↑Expr_Variable↑Arg↑Expr_FuncCall↓Arg↓Scalar_String↓integer'
    graph.find_specific_path_on_graph(path_to_find)
    graph.render('graph')
