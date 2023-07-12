import cparser

code = '''
int buffer_resolver(const unsigned char* buffer) {
    unsigned char buffer_length = buffer[0];

    if (2 <= buffer_length)
        return 0;

    if (MessageType_Hello == buffer[1]) {
        printf("Hello\n");
    } else if (MessageType_Execute == buffer[1]) {
        unsigned char* command_buffer = (unsigned char*)malloc(buffer_length - 1);

        memset(&command_buffer,0,buffer_length);
        memcpy(&command_buffer,&buffer[2],buffer_length - 2);

        execute_command(command_buffer);
    } else if (MessageType_Data == buffer[1]) {
        decrypt_data(&buffer[2],buffer_length - 2);
    }

    return 1;
}
'''

"""
————数据流分析————
"""

data = cparser.get_func_tree(code)
# data.nprint()

# for subnode_index in data.subnode :
#     print(subnode_index)

def get_function_parameters(ast_node):
    parameters_list = []

    for subnode_index in ast_node.subnode:
        if subnode_index[1].type == 'parallel':
            parameters_list += get_function_parameters(subnode_index[1])
        elif subnode_index[0] == 'parameters':
            parameters_list.append({
                'type': subnode_index[1].type,
                'value': subnode_index[1].value,
            })
        elif subnode_index[0].startswith('exp'):
            parameters_list.append({
                'type': subnode_index[1].type,
                'value': subnode_index[1].value,
            })

    return parameters_list


def recursive_find_call(ast_node, find_function_name):
    find_result = []

    for subnode_index in ast_node.subnode:
        if 'function_call' == subnode_index[1].type:
            if find_function_name == '*' or find_function_name == subnode_index[1].value:
                parameters_list = get_function_parameters(subnode_index[1])

                find_result.append((subnode_index, parameters_list))

        find_result += recursive_find_call(subnode_index[1], find_function_name)

    return find_result


def print_search_result(call_list):
    for call_index in call_list:
        ast_node_info = call_index[0]
        parameters_info = call_index[1]

        print('Call Function Name :', ast_node_info[1].value)
        print('  Function Argument :', parameters_info)

def resolve_strategy(user_search_strategy) :
    user_search_strategy = user_search_strategy.split('\n')
    check_strategy = []

    for user_search_strategy_index in user_search_strategy :
        strategy_record = user_search_strategy_index.strip()

        if not len(strategy_record) :
            continue

        search_function_name = strategy_record.split('(')[0].strip()
        search_parameter_string = strategy_record.split('(')[1].strip()
        search_parameter_string = search_parameter_string.split(')')[0].strip()
        search_parameter_list = []

        if len(search_parameter_string) :
            if not -1 == search_parameter_string.find(',') :
                search_parameter_string = search_parameter_string.split(',')
                parameter_index = -1

                for search_parameter_index in search_parameter_string :
                    check_parameter = search_parameter_index.strip()
                    parameter_index += 1

                    if not check_parameter == '*' :
                        continue

                    search_parameter_list.append(parameter_index)
            else :
                check_parameter = search_parameter_string.strip()

                if check_parameter == '*' :
                    search_parameter_list.append(0)

        check_strategy.append((search_function_name,search_parameter_list))

    return check_strategy

# 匹配
# find_function_call1 = recursive_find_call(data, 'execute_command')
# find_function_call2 = recursive_find_call(data, 'decrypt_data')
# print_search_result(find_function_call1)
# print_search_result(find_function_call2)

# 自定义匹配-函数
# search_strategy = '''
# execute_command(*)
# '''
# print(resolve_strategy(search_strategy))

# 自定义匹配-变量
# search_strategy = '''
# execute_command(*)
# memcpy(,*,)
# decrypt_data(*,*)
# '''
#
# search_strategy = resolve_strategy(search_strategy)
# search_record = {}
#
# for search_strategy_index in search_strategy :  #  Search Call by Strategy
#     find_function_name = search_strategy_index[0]
#     search_check_parameter_list = search_strategy_index[1]
#     find_function_call = recursive_find_call(data,find_function_name)
#
#     print_search_result(find_function_call)
#     search_record[find_function_name] = []
#
#     for call_index in find_function_call :  #  Find Match Strategy Call
#         ast_node_info = call_index[0]
#         parameters_list = call_index[1]
#
#         if search_check_parameter_list :
#             check_parameter_list = []
#
#             for search_check_parameter_index in search_check_parameter_list :  #  Filter Call Argument
#                 if len(parameters_list) <= search_check_parameter_index :
#                     continue
#
#                 target_search_parameter = parameters_list[search_check_parameter_index]
#
#                 if not target_search_parameter['type'] in ['variable','address_of'] :  #  Check this Argument is a Variant ..
#                     continue
#
#                 check_parameter_list.append(target_search_parameter)
#
#             if check_parameter_list :
#                 search_record[find_function_name].append((ast_node_info,check_parameter_list))
#         else :
#             search_record[find_function_name].append((ast_node_info,[]))
#
# print(search_record)

"""
————控制流分析————
"""

def get_condition(ast_node) :
    for index in ast_node.subnode :
        if 'condition' == index[0] :
            return index[1].value

    return False

def trance_control_flow_by_ast(start_node,target_node,trance_record) :
    code_record = []

    for node_object_index in start_node.subnode :
        if node_object_index == target_node :
            all_trance_record = trance_record + code_record
            control_flow_list = []

            for trance_record_index in all_trance_record :
                if trance_record_index[1].type == 'if' :
                    control_flow_list.append(get_condition(trance_record_index[1]))

            return (True,control_flow_list)

        code_record.append(node_object_index)

        is_search,sub_data = trance_control_flow_by_ast(node_object_index[1],target_node,trance_record + code_record)

        if is_search :
            control_flow_record_list = sub_data

            return (True,control_flow_record_list)

    return (False,code_record)


def search_call_by_strategy(search_strategy,code_object) :
    search_strategy = resolve_strategy(search_strategy)
    search_record = {}

    for search_strategy_index in search_strategy :  #  Search Call by Strategy
        find_function_name = search_strategy_index[0]
        search_check_parameter_list = search_strategy_index[1]
        find_function_call = recursive_find_call(code_object,find_function_name)
        search_record_list = []

        print_search_result(find_function_call)

        for call_index in find_function_call :  #  Find Match Strategy Call
            ast_node_info = call_index[0]
            parameters_list = call_index[1]

            if search_check_parameter_list :
                check_parameter_list = []

                for search_check_parameter_index in search_check_parameter_list :  #  Filter Call Argument
                    if len(parameters_list) <= search_check_parameter_index :
                        continue

                    target_search_parameter = parameters_list[search_check_parameter_index]

                    if not target_search_parameter['type'] in ['variable','address_of'] :  #  Check this Argument is a Variant ..
                        continue

                    check_parameter_list.append(target_search_parameter)

                if check_parameter_list :
                    search_record_list.append((ast_node_info,check_parameter_list))
            else :
                search_record_list.append((ast_node_info,[]))

        if search_record_list :  #  Fix This : If not found function call result so we let it empty (我总感觉这个语法不对。。。)
            search_record[find_function_name] = search_record_list

    return search_record

search_strategy = '''
execute_command(*)
'''
search_record = search_call_by_strategy(search_strategy,data)

print('Search Record :',search_record)

for search_record_index in search_record.keys() :
    functinon_name = search_record_index
    bingo_record_list = search_record[search_record_index]

    for bingo_record_index in bingo_record_list :
        print(trance_control_flow_by_ast(data,bingo_record_index[0],[]))