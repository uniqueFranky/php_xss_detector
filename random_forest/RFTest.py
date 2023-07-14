import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# 读取训练数据
data = pd.read_csv('train_dataset1.csv')

# 划分特征和标签
X = data['code']
y = data['label']

# 特征提取
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(X)

# 划分训练集和测试集
split = int(0.8 * len(data))
X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

# 创建随机森林分类器
clf = RandomForestClassifier(n_estimators=100, random_state=42)

# 训练模型
clf.fit(X_train, y_train)

# 在测试集上进行预测
y_pred = clf.predict(X_test)

# 评估模型性能
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

print(f'Accuracy: {accuracy:.4f}')
print(f'Precision: {precision:.4f}')
print(f'Recall: {recall:.4f}')
print(f'F1 Score: {f1:.4f}')

# 使用模型进行预测
new_code = [
    '<?php echo $_GET["name"]; ?>',
    '<?php $x = $_GET["input"]; echo $x; ?>',
    '<?php $user_input = $_POST["input"]; echo $user_input; ?>'
]

new_code_features = vectorizer.transform(new_code)
predicted_labels = clf.predict(new_code_features)

for code, label in zip(new_code, predicted_labels):
    print(f'Code: {code}')
    print(f'Predicted Label: {"Vulnerable" if label == 1 else "Not Vulnerable"}')
    print('---')
