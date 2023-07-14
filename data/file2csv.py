import os
import csv

# 定义输入文件夹路径和输出CSV文件路径
input_folder = './safe_ast'
output_csv = 'train_dataset1.csv'

# 获取输入文件夹中的所有文件列表
files = os.listdir(input_folder)

# 创建CSV文件并写入表头
with open(output_csv, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['code', 'label'])

    # 遍历每个文件，将内容写入CSV文件
    for file in files:
        input_file = os.path.join(input_folder, file)

        with open(input_file, 'r') as file:
            code = file.read().strip()

        label = 1  # 将标签设置为0

        writer.writerow([code, label])

print(f"CSV文件已生成：{output_csv}")
