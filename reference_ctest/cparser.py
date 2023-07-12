# -*- coding: UTF-8 -*-

# https://github.com/tscosine/cparser/blob/master/cparser.py

import re

bracket_count = 0
bracket_dict = {}
type_trans_count = 0
type_trans_dict = {}
string_count = 0
string_dict = {}


class ast_node:
    type = ''
    value = ''
    subnode = []
    # 节点类型编码
    cblock_coding = {'cblock': 1, 'if': 2, 'else': 3, 'while': 4, 'for': 5, 'switch': 6, 'case': 7, 'try': 8,
                     'catch': 9}
    # 表达式类型编码
    expression_coding = {
        'parallel': 10,
        'assign': 11,
        'assign_or': 12,
        'assign_xor': 13,
        'assign_and': 14,
        'assign_shift_right': 15,
        'assign_shift_left': 16,
        'assign_reduce': 17,
        'assign_add': 18,
        'assign_remain': 19,
        'assign_mult': 20,
        'assign_except': 21,
        'conditional_opt': 22,
        'or': 23,
        'and': 24,
        'or_bit': 25,
        'xor': 26,
        'and_bit': 27,
        'equal': 28,
        'not_equal': 29,
        'compare': 30,
        'compare_equal': 32,
        'shift_right': 34,
        'shift_left': 35,
        'reduce': 36,
        'add': 37,
        'mult': 38,
        'except': 39,
        'remain': 40,
        'typetrans': 41,
        '++': 42,
        '--': 43,
        'address_of': 44,
        'sizeof': 45,
        'negative': 46,
        'not': 47,
        '~': 48,
        'descend': 49,
        'ascend': 50,
        'choice_member(pointer)': 51,
        'choice_member(object)': 52,
        'get_element': 53,
        'return': 54,
        'goto': 55,
        'variable_define': 56,
        'function_call': 57,
        'variable': 58,
        'break': 59,
        'continue': 60,
        'constant': 61,
        'string': 62,
        'mark': 63
    }

    def __init__(self, type, value):
        self.value = value
        self.type = type
        self.subnode = []

    def add_subnode(self, linkname, subnode):
        '''
        添加子节点
        '''
        self.subnode.append([linkname, subnode])

    def has_node(self, linkname):
        '''
        判断是否存在某子节点
        '''
        for s in self.subnode:
            if s[0] == linkname:
                return True
        return False

    def nprint(self, level=0):
        '''
        打印树结构
        '''
        print('|-' * level + self.type + ' ' + self.value)
        for s in self.subnode:
            print('|-' * level + '(link)' + s[0])
            if s[1] != None:
                s[1].nprint(level + 1)

    def funccall_list(self):
        '''
        :return:调用的函数列表
        '''
        killlist = ['printf', 'scanf', 'getchar', 'putchar', 'time',
                    'strcpy', 'strcmp', '']  # 排除的函数
        result = []
        if self.type == 'function_call':
            result.append(self.value)
        for s in self.subnode:
            if s[1] != None:
                flist = s[1].funccall_list()
                result += flist
        if result.__len__() > 0:
            result = {}.fromkeys(result).keys()
        result = list(filter(lambda x: x not in killlist, result))
        return result

    def get_feature(self):
        '''
            将AST特征化,返回特征列表
            return：AST前序遍历序列
        '''
        feature = [self.type, ]
        if not self.type == 'variable_define':
            for sub in self.subnode:
                if sub[1] != None:
                    feature += sub[1].get_feature()
        feature_coding = []
        for f in feature:
            if self.cblock_coding.__contains__(f):
                feature_coding.append(self.cblock_coding[f])
            elif self.expression_coding.__contains__(f):
                feature_coding.append(self.expression_coding[f])
            else:
                feature_coding.append(f)
        return feature_coding

    def get_word_seq(self):
        '''
            AST节点按类型统计作为特征
            return: 返回AST词带特征
        '''
        feature_list = self.get_feature()
        seq = [0] * 63
        for f in feature_list:
            if type(f) is int:
                seq[f - 1] += 1
        return seq


def get_expression_tree(expression):
    global bracket_count
    global bracket_dict
    global type_trans_count
    global type_trans_dict
    global string_dict
    global string_count

    expression = expression.strip()  # 去除空格

    # The num of expression is base on priority of the opt
    exp1_1 = re.compile('([^\[]+)\[(.+)\]([^\]]*)')  # [],数组下标
    exp1_3 = re.compile('(\w+)\.(\w+)')  # .成员选择(对象)
    exp1_4 = re.compile('(\w+)->(\w+)')  # ->,成员选择(指针)
    exp1_5 = re.compile('(.+)\+\+(\W|$)')  # ++,后置自增
    exp1_6 = re.compile('(.+)--(\W|$)')  # --,后置自减

    exp2_1 = re.compile('(\W|^)-([^-=]{1}.*)')  # -,单目运算取负
    exp2_2 = re.compile('!([^=]{1}.*)')  # !,逻辑非
    exp2_3 = re.compile('~(.+)')  # ~,按位取反
    exp2_5 = re.compile('([^&]|^)&([^=]{1}.*)')  # &,取地址
    exp2_6 = re.compile('(\W|^)--(.+)')  # --,前置自减
    exp2_7 = re.compile('(\W|^)\+\+(.+)')  # ++,前置自增
    exp2_8 = re.compile('(\W|^)\((\w+)\)(.+)')  # 强制类型转换

    exp3_1 = re.compile('(.+)/([^=]{1}.*)')  # /
    exp3_2 = re.compile('(.+)\*([^=]{1}.*)')  # *
    exp3_3 = re.compile('(.+)%([^=]{1}.*)')  # %
    exp4_1 = re.compile('(.*[^+]{1})\+([^=+]{1}.*)')  # +
    exp4_2 = re.compile('(.*[^-]{1})-([^=\->]{1}.*)')  # -
    exp5_1 = re.compile('(.+)<<([^=]{1}.*)')  # <<,移位
    exp5_2 = re.compile('([^=]{1}.*)>>(.+)')  # >>,移位
    exp6_1 = re.compile('(.+)>=(.+)')  # >=,大于等于
    exp6_2 = re.compile('([^<]+)<=(.+)')  # <=,小于等于
    exp6_3 = re.compile('([^>-]+)>([^>]+)')  # >,大于
    exp6_4 = re.compile('([^<]+)<([^<]+)')  # <,小于
    exp7_1 = re.compile('(.+)==(.+)')  # ==,逻辑等于
    exp7_2 = re.compile('(.+)!=(.+)')  # !=,逻辑不等
    exp8 = re.compile('([^&]+)&([^&]+)')  # &,按位与
    exp9 = re.compile('(.+)\^(.+)')  # ^,按位异或
    exp10 = re.compile('([^\|]+)\|([^\|]+)')  # |,按位或
    exp11 = re.compile('(.+)&&(.+)')  # &&,逻辑与
    exp12 = re.compile('(.+)\|\|(.+)')  # ||,逻辑或
    exp13 = re.compile('(.+)\?(.+):(.+)')  # ?:,条件运算符

    exp14_1 = re.compile('(.+)/=(.+)')  # /=
    exp14_2 = re.compile('(.+)\*=(.+)')  # *=
    exp14_3 = re.compile('(.+)%=(.+)')  # %=
    exp14_4 = re.compile('(.*[^\+]{1})\+=(.+)')  # +=
    exp14_5 = re.compile('(.*[^-]{1})-=(.+)')  # -=
    exp14_6 = re.compile('(.+)<<=(.+)')  # <<=
    exp14_7 = re.compile('(.+)>>=(.+)')  # >>=
    exp14_8 = re.compile('(.+)&=(.+)')  # &=
    exp14_9 = re.compile('(.+)\^=(.+)')  # ^=
    exp14_10 = re.compile('(.+)\|=(.+)')  # |=
    exp14_11 = re.compile('(.*[^<>=]{1})=([^<>=]{1}.*)')  # =

    # 字符串常量替换
    changed = True
    while changed:
        changed = False
        for i in range(len(expression)):
            s = ''
            if expression[i] == '\"':
                start = i
                i += 1
                while expression[i] != '\"':
                    s += expression[i]
                    i += 1
                end = i + 1
                placeholder = '_string_const_replace_' + str(string_count)
                string_count += 1
                string_dict[placeholder] = ast_node('string', s)
                expression = expression[:start] + placeholder + expression[end:]
                changed = True
                break
            elif expression[i] == '\'':
                start = i
                i += 1
                while expression[i] != '\'':
                    s += expression[i]
                    i += 1
                end = i + 1
                placeholder = '_string_const_replace_' + str(string_count)
                string_count += 1
                string_dict[placeholder] = ast_node('string', s)
                expression = expression[:start] + placeholder + expression[end:]
                changed = True
                break

    # 括号,强制类型转换替换
    bracket_list = []
    changed = True
    while changed:
        changed = False
        for i in range(expression.__len__()):
            if expression[i] == '(':
                bracket_list.append((i, '('))
            if expression[i] == ')':
                if bracket_list.__len__() > 0:
                    start = bracket_list.pop()
                    if start[1] == ')':
                        # 语法出错处理
                        print('syntax error,extra ")"')
                    else:
                        changed = True
                        type_pattern = re.compile(
                            '(unsigned |long |register |static |extern |const |volatile |auto )*(short|int|long|float|double|char|void)( \*){0,1}')
                        if re.match(type_pattern, expression[start[0] + 1:i]):
                            # if expression[start[0] + 1:i] in CTYPE_LIST:
                            # 强制类型转换
                            placeholder = '_type_trans_replace_' + str(type_trans_count)
                            type_trans_count += 1
                            type_trans_dict[placeholder] = ast_node('trans_type', expression[start[0] + 1:i])
                            expression = expression[:start[0]] + placeholder + expression[i + 1:]
                        else:
                            # 普通括号
                            placeholder = '_bracket_replace_' + str(bracket_count)
                            bracket_count += 1
                            bracket_dict[placeholder] = get_expression_tree(expression[start[0] + 1:i])
                            expression = expression[:start[0]] + placeholder + expression[i + 1:]
                        break
                else:
                    # 语法出错处理
                    pass
                # print('syntax error,no ( to match')

    if re.match('return(.*)', expression):
        node = ast_node('return', '')
        exp_node = get_expression_tree(re.sub('return', '', expression))
        node.add_subnode('exp', exp_node)
        return node
    if re.match('goto(.*)', expression):
        node = ast_node('goto', '')
        exp_node = get_expression_tree(re.sub('goto', '', expression))
        node.add_subnode('exp', exp_node)
        return node
    # 变量定义识别
    if re.match('(\w+\s)*\w+\s.+', expression):
        node = ast_node('variable_define', '')
        explist = expression.split(' ')
        while len(explist) > 0:
            exp = explist.pop()
            if exp == 'struct':
                node.add_subnode('para', ast_node('isStruct', 'true'))
            elif exp == 'enum':
                node.add_subnode('para', ast_node('isEnum', 'true'))
            elif exp == 'union':
                node.add_subnode('para', ast_node('isUnion', 'true'))
            elif exp == 'unsigned':
                node.add_subnode('para', ast_node('isUnsigned', 'true'))
            elif exp == 'static':
                node.add_subnode('para', ast_node('isStatic', 'true'))
            elif exp == 'const':
                node.add_subnode('para', ast_node('isConst', 'true'))
            elif exp == 'Entern':
                node.add_subnode('para', ast_node('isEntern', 'true'))
            elif exp == 'register':
                node.add_subnode('para', ast_node('isRegister', 'true'))
            elif node.has_node('variablename'):
                node.add_subnode('typename', get_expression_tree(expression.split(' ')[-2]))
            else:
                if re.search('(\w+)\[(\d+)\]', exp):
                    rematch = re.search('(\w+)\[(\d+)\]', exp)
                    node.add_subnode('para', ast_node('isArray', 'true'))
                    node.add_subnode('para', ast_node('ArraySize', str(rematch.group(2))))
                    node.add_subnode('variablename', ast_node('variablename', rematch.group(1)))
                else:
                    node.add_subnode('variablename', get_expression_tree(exp))

        return node

    # ,并列表达式
    if re.search(',', expression):
        node = ast_node('parallel', '')
        count = 0
        for exp in expression.split(','):
            count += 1
            node.add_subnode('exp' + str(count), get_expression_tree(exp))
        return node

    if re.search(exp13, expression):
        rematch = re.search(exp13, expression)
        node = ast_node('conditional_opt', rematch.group())
        node.add_subnode('conditon', get_expression_tree(rematch.group(1)))
        node.add_subnode('op1', get_expression_tree(rematch.group(2)))
        node.add_subnode('op2', get_expression_tree(rematch.group(3)))
        return node
    elif re.search(exp14_1, expression):
        rematch = re.search(exp14_1, expression)
        node = ast_node('assign_except', rematch.group())
        node.add_subnode('left', get_expression_tree(rematch.group(1)))
        node.add_subnode('right', get_expression_tree(rematch.group(2)))
        return node
    elif re.search(exp14_2, expression):
        rematch = re.search(exp14_2, expression)
        node = ast_node('assign_mult', rematch.group())
        node.add_subnode('left', get_expression_tree(rematch.group(1)))
        node.add_subnode('right', get_expression_tree(rematch.group(2)))
        return node
    elif re.search(exp14_3, expression):
        rematch = re.search(exp14_3, expression)
        node = ast_node('assign_remain', rematch.group())
        node.add_subnode('left', get_expression_tree(rematch.group(1)))
        node.add_subnode('right', get_expression_tree(rematch.group(2)))
        return node
    elif re.search(exp14_4, expression):
        rematch = re.search(exp14_4, expression)
        node = ast_node('assign_add', rematch.group())
        node.add_subnode('left', get_expression_tree(rematch.group(1)))
        node.add_subnode('right', get_expression_tree(rematch.group(2)))
        return node
    elif re.search(exp14_5, expression):
        rematch = re.search(exp14_5, expression)
        node = ast_node('assign_reduce', rematch.group())
        node.add_subnode('left', get_expression_tree(rematch.group(1)))
        node.add_subnode('right', get_expression_tree(rematch.group(2)))
        return node
    elif re.search(exp14_6, expression):
        rematch = re.search(exp14_6, expression)
        node = ast_node('assign_shift_left', rematch.group())
        node.add_subnode('left', get_expression_tree(rematch.group(1)))
        node.add_subnode('right', get_expression_tree(rematch.group(2)))
        return node
    elif re.search(exp14_7, expression):
        rematch = re.search(exp14_7, expression)
        node = ast_node('assign_shift_right', rematch.group())
        node.add_subnode('left', get_expression_tree(rematch.group(1)))
        node.add_subnode('right', get_expression_tree(rematch.group(2)))
        return node
    elif re.search(exp14_8, expression):
        rematch = re.search(exp14_8, expression)
        node = ast_node('assign_and', rematch.group())
        node.add_subnode('left', get_expression_tree(rematch.group(1)))
        node.add_subnode('right', get_expression_tree(rematch.group(2)))
        return node
    elif re.search(exp14_9, expression):
        rematch = re.search(exp14_9, expression)
        node = ast_node('assign_xor', rematch.group())
        node.add_subnode('left', get_expression_tree(rematch.group(1)))
        node.add_subnode('right', get_expression_tree(rematch.group(2)))
        return node
    elif re.search(exp14_10, expression):
        rematch = re.search(exp14_10, expression)
        node = ast_node('assign_or', rematch.group())
        node.add_subnode('left', get_expression_tree(rematch.group(1)))
        node.add_subnode('right', get_expression_tree(rematch.group(2)))
        return node
    elif re.search(exp14_11, expression):
        rematch = re.search(exp14_11, expression)
        node = ast_node('assign', rematch.group())
        node.add_subnode('left', get_expression_tree(rematch.group(1)))
        node.add_subnode('right', get_expression_tree(rematch.group(2)))
        return node

    elif re.search(exp12, expression):
        rematch = re.search(exp12, expression)
        node = ast_node('or', rematch.group())
        node.add_subnode('exp1', get_expression_tree(rematch.group(1)))
        node.add_subnode('exp2', get_expression_tree(rematch.group(2)))
        return node

    elif re.search(exp11, expression):
        rematch = re.search(exp11, expression)
        node = ast_node('and', rematch.group())
        node.add_subnode('exp1', get_expression_tree(rematch.group(1)))
        node.add_subnode('exp2', get_expression_tree(rematch.group(2)))
        return node

    elif re.search(exp10, expression):
        rematch = re.search(exp10, expression)
        node = ast_node('or_bit', rematch.group())
        node.add_subnode('exp1', get_expression_tree(rematch.group(1)))
        node.add_subnode('exp2', get_expression_tree(rematch.group(2)))
        return node

    elif re.search(exp9, expression):
        rematch = re.search(exp9, expression)
        node = ast_node('xor', rematch.group())
        node.add_subnode('exp1', get_expression_tree(rematch.group(1)))
        node.add_subnode('exp2', get_expression_tree(rematch.group(2)))
        return node

    elif re.search(exp8, expression):
        rematch = re.search(exp8, expression)
        node = ast_node('and_bit', rematch.group())
        node.add_subnode('exp1', get_expression_tree(rematch.group(1)))
        node.add_subnode('exp2', get_expression_tree(rematch.group(2)))
        return node

    elif re.search(exp7_1, expression):
        rematch = re.search(exp7_1, expression)
        node = ast_node('equal', rematch.group())
        node.add_subnode('exp1', get_expression_tree(rematch.group(1)))
        node.add_subnode('exp2', get_expression_tree(rematch.group(2)))
        return node
    elif re.search(exp7_2, expression):
        rematch = re.search(exp7_2, expression)
        node = ast_node('not equal', rematch.group())
        node.add_subnode('exp1', get_expression_tree(rematch.group(1)))
        node.add_subnode('exp2', get_expression_tree(rematch.group(2)))
        return node

    elif re.search(exp6_1, expression):
        rematch = re.search(exp6_1, expression)
        node = ast_node('compare_equal', rematch.group())
        node.add_subnode('exp1', get_expression_tree(rematch.group(1)))
        node.add_subnode('exp2', get_expression_tree(rematch.group(2)))
        return node
    elif re.search(exp6_2, expression):
        rematch = re.search(exp6_2, expression)
        node = ast_node('compare_equal', rematch.group())
        node.add_subnode('exp1', get_expression_tree(rematch.group(1)))
        node.add_subnode('exp2', get_expression_tree(rematch.group(2)))
        return node
    elif re.search(exp6_3, expression):
        rematch = re.search(exp6_3, expression)
        node = ast_node('compare', rematch.group())
        node.add_subnode('exp1', get_expression_tree(rematch.group(1)))
        node.add_subnode('exp2', get_expression_tree(rematch.group(2)))
        return node
    elif re.search(exp6_4, expression):
        rematch = re.search(exp6_4, expression)
        node = ast_node('compare', rematch.group())
        node.add_subnode('exp1', get_expression_tree(rematch.group(1)))
        node.add_subnode('exp2', get_expression_tree(rematch.group(2)))
        return node

    elif re.search(exp5_1, expression):
        rematch = re.search(exp5_1, expression)
        node = ast_node('shift_left', rematch.group())
        node.add_subnode('exp1', get_expression_tree(rematch.group(1)))
        node.add_subnode('exp2', get_expression_tree(rematch.group(2)))
        return node
    elif re.search(exp5_2, expression):
        rematch = re.search(exp5_2, expression)
        node = ast_node('shift_right', rematch.group())
        node.add_subnode('exp1', get_expression_tree(rematch.group(1)))
        node.add_subnode('exp2', get_expression_tree(rematch.group(2)))
        return node

    elif re.search(exp4_1, expression):
        rematch = re.search(exp4_1, expression)
        node = ast_node('add', rematch.group())
        node.add_subnode('exp1', get_expression_tree(rematch.group(1)))
        node.add_subnode('exp2', get_expression_tree(rematch.group(2)))
        return node
    elif re.search(exp4_2, expression):
        rematch = re.search(exp4_2, expression)
        node = ast_node('reduce', rematch.group())
        node.add_subnode('exp1', get_expression_tree(rematch.group(1)))
        node.add_subnode('exp2', get_expression_tree(rematch.group(2)))
        return node

    elif re.search(exp3_1, expression):
        rematch = re.search(exp3_1, expression)
        node = ast_node('except', rematch.group())
        node.add_subnode('exp1', get_expression_tree(rematch.group(1)))
        node.add_subnode('exp2', get_expression_tree(rematch.group(2)))
        return node
    elif re.search(exp3_2, expression):
        rematch = re.search(exp3_2, expression)
        node = ast_node('mult', rematch.group())
        node.add_subnode('exp1', get_expression_tree(rematch.group(1)))
        node.add_subnode('exp2', get_expression_tree(rematch.group(2)))
        return node
    elif re.search(exp3_3, expression):
        rematch = re.search(exp3_3, expression)
        node = ast_node('remain', rematch.group())
        node.add_subnode('exp1', get_expression_tree(rematch.group(1)))
        node.add_subnode('exp2', get_expression_tree(rematch.group(2)))
        return node

    elif re.search(exp2_1, expression):
        rematch = re.search(exp2_1, expression)
        node = ast_node('negative', rematch.group())
        node.add_subnode('exp', get_expression_tree(rematch.group(2)))
        return node
    elif re.search(exp2_2, expression):
        rematch = re.search(exp2_2, expression)
        node = ast_node('not', rematch.group())
        node.add_subnode('exp', get_expression_tree(rematch.group(1)))
        return node
    elif re.search(exp2_3, expression):
        rematch = re.search(exp2_3, expression)
        node = ast_node('~', rematch.group())
        node.add_subnode('exp', get_expression_tree(rematch.group(1)))
        return node
    elif re.search(exp2_5, expression):
        rematch = re.search(exp2_5, expression)
        node = ast_node('address_of', rematch.group())
        node.add_subnode('exp', get_expression_tree(rematch.group(2)))
        return node
    elif re.search(exp2_6, expression):
        rematch = re.search(exp2_6, expression)
        node = ast_node('--', rematch.group())
        node.add_subnode('exp', get_expression_tree(rematch.group(1)))
        return node
    elif re.search(exp2_7, expression):
        rematch = re.search(exp2_7, expression)
        node = ast_node('++', rematch.group())
        node.add_subnode('exp', get_expression_tree(rematch.group(1)))
        return node
    elif re.search(exp2_8, expression):
        rematch = re.search(exp2_8, expression)
        node = ast_node('typetrans', rematch.group())
        node.add_subnode('type', get_expression_tree(rematch.group(2)))
        node.add_subnode('exp', get_expression_tree(rematch.group(3)))
        return node
    elif re.search(exp1_1, expression):
        rematch = re.search(exp1_1, expression)
        node = ast_node('get_element', rematch.group())
        node.add_subnode('arr', get_expression_tree(rematch.group(1)))
        node.add_subnode('index', get_expression_tree(rematch.group(2)))
        return node
    elif re.search(exp1_3, expression):
        rematch = re.search(exp1_3, expression)
        node = ast_node('choice_member(object)', rematch.group())
        node.add_subnode('object', get_expression_tree(rematch.group(1)))
        node.add_subnode('member', get_expression_tree(rematch.group(2)))
        return node
    elif re.search(exp1_4, expression):
        rematch = re.search(exp1_4, expression)
        node = ast_node('choice_member(pointer)', rematch.group())
        node.add_subnode('pointer', get_expression_tree(rematch.group(1)))
        node.add_subnode('member', get_expression_tree(rematch.group(2)))
        return node
    elif re.search(exp1_5, expression):
        rematch = re.search(exp1_5, expression)
        node = ast_node('ascend', rematch.group())
        node.add_subnode('exp', get_expression_tree(rematch.group(1)))
        return node
    elif re.search(exp1_6, expression):
        rematch = re.search(exp1_6, expression)
        node = ast_node('descend', rematch.group())
        node.add_subnode('exp', get_expression_tree(rematch.group(1)))
        return node

    # 强制类型转换
    elif re.match('(_type_trans_replace_\d+)(.*)', expression):
        rematch = re.match('(_type_trans_replace_\d+)(.*)', expression)
        if type_trans_dict.__contains__(rematch.group(1)):
            node = type_trans_dict[rematch.group(1)]
            node.add_subnode('exp', get_expression_tree(rematch.group(2)))
            return node
        else:
            return ast_node('variable', expression)

    # sizeof()
    elif re.match('sizeof(_bracket_replace_\d+)', expression):
        bracket_name = re.match('sizeof(_bracket_replace_\d+)', expression).group(1)
        if bracket_dict.__contains__(bracket_name):
            node = ast_node('sizeof', '')
            node.add_subnode('exp', bracket_dict[bracket_name])
            return node
        else:
            return ast_node('variable', expression)

    # funciton call
    elif re.match('(\w+)(_bracket_replace_\d+)', expression):
        rematch = re.match('(\w+)(_bracket_replace_\d+)', expression)
        bracket_name = rematch.group(2)
        if bracket_dict.__contains__(bracket_name):
            node = ast_node('function_call', rematch.group(1))
            # node.add_subnode('function',get_expression_tree(rematch.group(1)))
            if bracket_dict[bracket_name] != None:
                node.add_subnode('parameters', bracket_dict[bracket_name])
            return node
        else:
            return ast_node('variable', expression)

    # 普通括号
    elif re.match('_bracket_replace_\d+', expression):
        if bracket_dict.__contains__(expression):
            return bracket_dict[expression]
        else:
            return ast_node('variable', expression)

    elif re.match('_string_const_replace_\d+', expression):
        if string_dict.__contains__(expression):
            return string_dict[expression]
        else:
            return ast_node('variable', expression)

    elif re.match('break', expression):
        return ast_node('break', '')
    elif re.match('continue', expression):
        return ast_node('continue', '')
    # 常量
    elif re.match('\d+', expression):
        return ast_node('constant', expression)
    elif expression.__len__() <= 0:
        return None
    else:
        return ast_node('variable', expression)


def kill_Macro_Definition(block):
    '''
    删除宏定义
    :param block:
    :return:
    '''
    block = re.sub('#\w+\n', '', block)
    # note_index = []
    # for i in range(len(block)):
    # 	start = 0
    # 	end = 0
    # 	if re.match('#', block[i]):
    # 		start = i
    # 		while i < block.__len__():
    # 			i += 1
    # 			end = i
    # 			if block[i] == '\n':
    # 				note_index.append((start, end))
    # 				break
    # 	if end == block.__len__():
    # 		note_index.append((start,end-1))
    # 		break
    # while note_index.__len__() > 0:
    # 	start, end = note_index.pop()
    # 	block = block[:start] + block[end + 1:]
    return block


def kill_note(block):
    '''
    删除注释
    :param block:
    :return:
    '''
    note_index = []

    ifdef_pattern = re.compile('#ifdef.+\n')
    block = re.sub(ifdef_pattern, '', block)

    sameline_pattern = re.compile('\\\s*\n')
    block = re.sub(sameline_pattern, '', block)
    # 标记注释
    for i in range(len(block)):
        start = 0
        end = 0
        if re.match('//', block[i:i + 2]):
            start = i
            while block[i] != '\n' and i < block.__len__():
                i += 1
            end = i
            note_index.append((start, end))
        elif re.match('/\*', block[i:i + 2]):
            start = i
            while not re.match('\*/', block[i:i + 2]):
                i += 1
            end = i + 1
            note_index.append((start, end))

    # 删除注释
    while note_index.__len__() > 0:
        start, end = note_index.pop()
        block = block[:start] + block[end + 1:]

    return block


def kill_space(block):
    '''
    删除空格
    :param block:
    :return:
    '''
    block = re.sub('\t|\n', ' ', block)  # 换行符和制表符替换为空格
    asm_pattern = re.compile('asm volatile \(.*\);')
    block = re.sub(asm_pattern, '', block)
    asm_pattern = re.compile('__asm__ __volatile__ \(.*\);')
    block = re.sub(asm_pattern, '', block)
    # 清除多余的空格
    finish = False
    while not finish:
        finish = True
        i = 0
        while i < block.__len__() - 1:
            if block[i] == ' ':
                if re.match('\w|\d|&|\*', block[i - 1]) and re.match('[^\w\d&\*]', block[i + 1]):
                    block = block[:i] + block[i + 1:]
                    finish = False
                elif re.match('[^\w\d&\*]', block[i - 1]) and re.match('\w|\d|&|\*', block[i + 1]):
                    block = block[:i] + block[i + 1:]
                    finish = False
                elif re.match('\'|\"', block[i - 1]) or re.match('\"|\'', block[i + 1]):
                    block = block[:i] + block[i + 1:]
                    finish = False
                elif re.match('{|}', block[i + 1]) or re.match('{|}', block[i - 1]):
                    block = block[:i] + block[i + 1:]
                    finish = False
                elif re.match('\(', block[i + 1]) or re.match('\)', block[i - 1]):
                    block = block[:i] + block[i + 1:]
                    finish = False
                elif re.match('\[', block[i + 1]) or re.match('\]', block[i - 1]):
                    block = block[:i] + block[i + 1:]
                    finish = False
            i += 1

    # macro_function_pattern = re.compile('(\w+)(\([^\(\)]*\))[^;\{]')
    # changed = True
    # while re.search(macro_function_pattern,block) and changed:
    # 	changed = False
    # 	it = re.finditer(macro_function_pattern,block)
    # 	for match in it:
    # 		if re.findall('\"',match.group(2)).__len__() % 2 == 0 and re.findall("\'",match.group(2)).__len__() %2 ==0:
    # 			start,end = re.search(macro_function_pattern,block).span(0)
    # 			block = block[:start] + block[end-1:]
    # 			changed = True
    # 			break
    return block


def Standardization(block):
    '''
    标准化代码块
    :param block:
    :return:
    '''
    block = kill_note(block)  # 删除注释
    block = kill_space(block)  # 删除空格
    block = kill_Macro_Definition(block)  # 删除宏定义
    return block


def get_switch_node(switch_body):
    '''
    解析switch语句
    :param switch_body:switch语句
    :return:AST节点列表
    '''
    result = []
    pattern1 = re.compile('case (.+?):(.*?break;)')
    pattern2 = re.compile('default:(.*break;)')

    for m in re.findall(pattern1, switch_body):
        case_node = ast_node('case', '')
        case_node.add_subnode('condition', get_expression_tree(m[0]))
        case_node.add_subnode('body', get_block_tree(m[1]))
        result.append(case_node)

    for m in re.findall(pattern2, switch_body):
        case_node = ast_node('case', 'default')
        case_node.add_subnode('body', get_block_tree(m))
        result.append(case_node)

    return result


def get_next_block(block, begin, qouta_dict, bracket_dict):
    '''
    获取下一个代码块的位置
    :param block:		代码块
    :param begin:		开始搜索的位置
    :param qouta_dict:	引号跳转字典
    :param bracket_dict:括号跳转字典
    :return:代码块第一个字符位置,代码块最后一个字符位置.代码块之后的第一个字符位置
    '''
    if block[begin] == '(':
        begin = bracket_dict[begin] + 1
    i = begin
    count = 0
    try:
        while i < len(block):
            if block[i] == '\'' or block[i] == '\"':
                i = qouta_dict[i]
            elif block[i] == '{':
                count += 1
            elif block[i] == '}':
                count -= 1
                if count == 0:
                    return (begin + 1, i - 1, i + 1)
            elif block[i] == ';' and count == 0:
                return (begin, i, i + 1)
            i += 1
        if count == 0:
            return (begin, i - 1, i - 1)
        else:
            return (begin + 1, i - 1, i - 1)
    except BaseException as e:
        print(e)
        with open('/home/cosine/mygit/error_' + block[begin:begin + 10], 'w') as f:
            f.write(block[:begin])
            f.write('---------------------------')
            f.write(block[begin:])
        return (begin, begin, begin)


def get_block_tree(block, blocktype='cblock'):
    '''
    为代码块生成AST节点
    :param block:		代码块
    :param blocktype:	代码块名
    :return:			AST节点
    '''
    qouta1 = -1
    qouta2 = -1
    qouta_dict = {}
    for i in range(block.__len__()):
        if block[i] == '\'' and block[i - 1] != '\\':
            if qouta1 > 0:
                qouta_dict[qouta1] = i
                qouta_dict[i] = qouta1
                qouta1 = -1
            else:
                qouta1 = i
        if block[i] == '\"' and block[i - 1] != '\\':
            if qouta2 > 0:
                qouta_dict[qouta2] = i
                qouta_dict[i] = qouta2
                qouta2 = -1
            else:
                qouta2 = i
    '''
    生成括号对照词典，保存括号配对信息
    '''
    parenthesis_stack = []  # ()
    bracket_stack = []  # []
    brace_stack = []  # {}
    bracket_dict = {}  # all of theme
    i = 0
    while i < len(block):

        if block[i] == '\'' or block[i] == '\"':
            if qouta_dict.__contains__(i):
                i = qouta_dict[i]
            else:
                pass
        if block[i] == '(':
            parenthesis_stack.append((i, '('))
        elif block[i] == ')':
            if parenthesis_stack.__len__() <= 0 or parenthesis_stack[-1][1] != '(':
                pass
            else:
                match = parenthesis_stack.pop()
                bracket_dict[match[0]] = i
                bracket_dict[i] = match[0]

        if block[i] == '[':
            bracket_stack.append((i, '['))
        elif block[i] == ']':
            if bracket_stack.__len__() <= 0 or bracket_stack[-1][1] != '[':
                pass
            else:
                match = bracket_stack.pop()
                bracket_dict[match[0]] = i
                bracket_dict[i] = match[0]

        if block[i] == '{':
            brace_stack.append((i, '{'))
        elif block[i] == '}':
            if brace_stack.__len__() <= 0 or brace_stack[-1][1] != '{':
                pass
            else:
                match = brace_stack.pop()
                bracket_dict[match[0]] = i
                bracket_dict[i] = match[0]
        i += 1

    '''
    开始分析
    '''
    expression = ''
    expression_count = 0
    root_node = ast_node(blocktype, '')
    i = 0
    while i < len(block):
        # if语句
        if block[i] == '(' and expression == 'if':
            # 条件语句
            ifnode = ast_node('if', '')
            condition_end = bracket_dict[i]
            condition = block[i + 1:condition_end]
            condition_node = get_expression_tree(condition)
            ifnode.add_subnode('condition', condition_node)
            i = condition_end + 1

            # if块内语句
            bstart, bend, i = get_next_block(block, i, qouta_dict, bracket_dict)
            ifblockbody = block[bstart:bend + 1]
            ifblock_node = get_block_tree(ifblockbody)
            ifnode.add_subnode('ifbody', ifblock_node)

            # 匹配else块
            while i < block.__len__():
                if block[i:i + 7] == 'else if':
                    i += 7
                    assert block[i] == '('
                    else_condition = block[i + 1:bracket_dict[i]]
                    i = bracket_dict[i] + 1

                elif block[i:i + 4] == 'else':
                    else_condition = None
                    i += 4
                else:
                    break

                bstart, bend, i = get_next_block(block, i, qouta_dict, bracket_dict)
                elseblock = block[bstart:bend + 1]

                elseblock_node = get_block_tree(elseblock, 'else')
                if else_condition != None:
                    elseblock_node.add_subnode('condition', get_expression_tree(else_condition))
                ifnode.add_subnode('elsebody', elseblock_node)
            root_node.add_subnode('if', ifnode)
            expression = ''


        elif re.match('\s*try', expression):
            try_node = ast_node('try', '')
            bstart, bend, i = get_next_block(block, i, qouta_dict, bracket_dict)
            trybody = block[bstart:bend + 1]
            trybody_node = get_block_tree(trybody)
            try_node.add_subnode('try', trybody_node)
            if block[i:i + 5] == 'catch':
                i = i + 5
                bstart, bend, i = get_next_block(block, i, qouta_dict, bracket_dict)
                catchbody = block[bstart:bend + 1]
                catchbody_node = get_block_tree(catchbody)
                try_node.add_subnode('catch', catchbody_node)
            root_node.add_subnode('try_catch', try_node)
            expression = ''

        # 检索匹配while代码块
        elif block[i] == '(' and re.match('\s*while', expression):
            whilenode = ast_node('while', '')
            condition_end = bracket_dict[i]
            condition = block[i + 1:condition_end]
            i = condition_end + 1
            while_condition_node = get_expression_tree(condition)
            whilenode.add_subnode('condition', while_condition_node)

            bstart, bend, i = get_next_block(block, i, qouta_dict, bracket_dict)
            circlebody = block[bstart:bend + 1]  # 循环体

            circle_node = get_block_tree(circlebody)
            whilenode.add_subnode('loop', circle_node)
            root_node.add_subnode('while', whilenode)
            expression = ''

        # 检索匹配for代码块
        elif block[i] == '(' and re.match('\s*for', expression):
            fornode = ast_node('for', '')
            for_end = bracket_dict[i]
            condition = block[i + 1:for_end]
            i = for_end + 1
            condition = condition.split(';')
            for_condition_node1 = get_expression_tree(condition[0])
            for_condition_node2 = get_expression_tree(condition[1])
            for_condition_node3 = get_expression_tree(condition[2])
            fornode.add_subnode('condition_init', for_condition_node1)
            fornode.add_subnode('condition_end', for_condition_node2)
            fornode.add_subnode('condition_iteration', for_condition_node3)

            bstart, bend, i = get_next_block(block, i, qouta_dict, bracket_dict)
            circlebody = block[bstart:bend + 1]  # 循环体

            circle_node = get_block_tree(circlebody)
            fornode.add_subnode('loop', circle_node)
            root_node.add_subnode('for', fornode)
            expression = ''

        # switch代码块
        elif block[i] == '(' and expression == 'switch':
            switch_node = ast_node('switch', '')
            switch_condition_end = bracket_dict[i]
            switch_condition = block[i + 1:switch_condition_end]
            switch_node.add_subnode('condition', get_expression_tree(switch_condition))

            i = switch_condition_end + 1
            switch_body_end = bracket_dict[i]
            switch_body = block[i + 1:switch_body_end]
            switch_node_list = get_switch_node(switch_body)
            for node in switch_node_list:
                switch_node.add_subnode('case', node)
            root_node.add_subnode('switch', switch_node)
            expression = ''
            i = switch_body_end + 1

        # 普通语句
        elif block[i] == ';':
            # print('get expression:'+expression)
            expression_node = get_expression_tree(expression)
            root_node.add_subnode('exp' + str(expression_count), expression_node)
            expression = ''
            expression_count += 1
            i += 1

        elif block[i] == ':' and expression.__len__() < 20:
            expression_node = ast_node('mark', expression)
            root_node.add_subnode('mark' + str(expression_count), expression_node)
            expression = ''
            expression_count += 1
            i += 1

        # 读入字符
        else:
            # print(block[i:i+200])
            # print('---------------')
            if (block[i] == '\'' or block[i] == '\"') and block[i - 1] != '\\':
                expression += block[i:qouta_dict[i] + 1]
                i = qouta_dict[i] + 1
            else:
                expression += block[i]
                i += 1
    return root_node


def get_func_tree(funcbody):
    '''
    为函数体生成AST
    :param funcbody:函数体
    :return:		AST根节点
    '''
    funcbody = Standardization(funcbody)
    start = 0
    end = 0
    for i in range(funcbody.__len__()):
        if funcbody[i] == "{":
            start = i
            break
    for i in range(funcbody.__len__())[::-1]:
        if funcbody[i] == "}":
            end = i
            break
    funcname = funcbody[:start]
    funcbody = funcbody[start + 1:end]

    funcbodynode = get_block_tree(funcbody, '')
    return funcbodynode


def get_funcbody(filebody, functionname):
    '''
    :param filebody:文件内容
    :param functionname:函数名
    :return:函数内容
    '''
    count = 0
    status = 0
    if type(filebody) is bytes:
        filebody = filebody.decode('UTF-8')
    filebody = kill_note(filebody)
    if re.search(functionname, filebody):
        start = re.search(functionname, filebody).start(0)
        end = re.search(functionname, filebody).end(0)
        while start > 0:
            start -= 1
            if filebody[start] == '}' or filebody[start] == ';':
                break
        while end < filebody.__len__():
            if status == -2:
                if filebody[end:end + 2] == '*/':
                    status = 0
            elif status == -1:
                if filebody[end] == '\n':
                    status = 0
            elif status == 1:
                if filebody[end] == '\'':
                    status = 0
            elif status == 2:
                if filebody[end] == '\"':
                    status = 0
            elif status == 0:
                if filebody[end] == ";" and count == 0:
                    return None
                if filebody[end:end + 2] == '//':
                    status = -1
                elif filebody[end:end + 2] == '/*':
                    status = -2
                elif filebody[end] == '\'':
                    status = 1
                elif filebody[end] == '\"':
                    status = 2
                elif filebody[end] == '{':
                    count += 1
                elif filebody[end] == '}':
                    count -= 1
                    if count == 0:
                        break
            end += 1
        # print(count,status,end)
        return filebody[start + 1:end + 1]
    else:
        return None