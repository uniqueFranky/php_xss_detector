import graphviz
import jsonToTree
import json

class ASTGraph:
    def __init__(self, dot) -> None:
        self.graph = dot
        self.edges = []
        self.edges_of_labels = []
        self.vocab = {}
        self.cnt = 0
        self.destinations_for = {}
        self.
    
    def node(self, label: str):
        self.cnt += 1
        self.graph.node(str(self.cnt), label)
        self.vocab.update({self.cnt: label})

    def edge(self, st: int, ed: int):
        self.graph.edge(str(st), str(ed))
        self.edges.append((st, ed))
        self.edges_of_labels.append((self.vocab[st], self.vocab[ed]))
        if st in self.destinations_for:
            self.destinations_for[st].append(ed)
        else:
            self.destinations_for.update({st: [ed]})

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

with open('ast.json', 'r') as f:
    graph = build_graph_by_json(f.read())
    
    graph.render('graph')
    print(graph.get_destinations())