import subprocess


# 获取php部分的代码
def get_php_code(input_file, output_file):

    """ 使用示例
    input_file = 'source.php'
    output_file = 'source_pre.php'
    get_php_code(input_file, output_file)
    """

    with open(input_file, 'r') as file:
        content = file.read()

    start_tag = '<?php'
    end_tag = '?>'

    start_index = content.find(start_tag)
    end_index = content.rfind(end_tag)

    if start_index != -1 and end_index != -1 and start_index < end_index:
        php_code = content[start_index + len(start_tag):end_index].strip()

        with open(output_file, 'w') as file:
            file.write(php_code)

def get_php_ast(output_filename):
    # 执行 "php filename.php" 命令
    # subprocess报错去subprocess.py修改shell=Flase改为True
    #subprocess.Popen(["cmd", "/c", "dir", "c:\\Users"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result = subprocess.run(['D:\\CTFtools\\web\\phpstudyv8.1\\phpstudy_pro\\Extensions\\php\\php7.3.4nts\\php.exe', 'E:\\notes\\NUS\\DOTA\\code\\php_xss_detector\\test\\phpporser.php'], capture_output=True, text=True)

    # 检查执行结果
    if result.returncode == 0:
        # 打印命令输出
        print(result.stdout)
    else:
        # 打印错误信息
        print(result.stderr)

    with open(output_filename, 'w') as file:
        file.write(result.stdout)


output_filename = "ast_output"
get_php_ast(output_filename)
