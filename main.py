import model
import subprocess
import preprocessing
import json

# code = preprocessing.read_php_code_from_file('safe/CWE_79__array-GET__CAST-cast_float__Unsafe_use_untrusted_data-attribute_Name.php')
# parser = subprocess.run(['php', 'parser.php', code], check=True, stdout=subprocess.PIPE)
# ast_json = parser.stdout.decode()
# ast = json.loads(ast_json)
model.train(vocab_size=167, embedding_size=300, hidden_size=500, num_layers=30, output_size=2, num_epoch=200, lr=0.01)
