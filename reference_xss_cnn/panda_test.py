"""
https://www.runoob.com/pandas/pandas-tutorial.html

读数据
    pd.read_csv(filename)                   读取 CSV 文件；
    pd.read_excel(filename)	                读取 Excel 文件；
    pd.read_sql(query, connection_object)	从 SQL 数据库读取数据；
    pd.read_json(json_string)	            从 JSON 字符串中读取数据；
    pd.read_html(url)	                    从 HTML 页面中读取数据。

查数据
    df.head(n)	    显示前 n 行数据；
    df.tail(n)	    显示后 n 行数据；
    df.info()	    显示数据的信息，包括列名、数据类型、缺失值等；
    df.describe()	显示数据的基本统计信息，包括均值、方差、最大值、最小值等；
    df.shape	    显示数据的行数和列数。

数据清洗
    df.dropna()	                        删除包含缺失值的行或列；
    df.fillna(value)	                将缺失值替换为指定的值；
    df.replace(old_value, new_value)	将指定值替换为新值；
    df.duplicated()	                    检查是否有重复的数据；
    df.drop_duplicates()	            删除重复的数据。

数据选择和切片
    df[column_name]	                                选择指定的列；
    df.loc[row_index, column_name]	                通过标签选择数据；
    df.iloc[row_index, column_index]	            通过位置选择数据；
    df.ix[row_index, column_name]	                通过标签或位置选择数据；
    df.filter(items=[column_name1, column_name2])	选择指定的列；
    df.filter(regex='regex')	                    选择列名匹配正则表达式的列；
    df.sample(n)	                                随机选择 n 行数据。

排序
    df.sort_values(column_name)	                                            按照指定列的值排序；
    df.sort_values([column_name1, column_name2], ascending=[True, False])	按照多个列的值排序；
    df.sort_index()	                                                        按照索引排序。

数据分组和聚合
    df.groupby(column_name)	                        按照指定列进行分组；
    df.aggregate(function_name)	                    对分组后的数据进行聚合操作；
    df.pivot_table(values, index, columns, aggfunc)	生成透视表。

数据合并
    pd.concat([df1, df2])	            将多个数据框按照行或列进行合并；
    pd.merge(df1, df2, on=column_name)	按照指定列将两个数据框进行合并。

选择和过滤
    df.loc[row_indexer, column_indexer]	    按标签选择行和列。
    df.iloc[row_indexer, column_indexer]	按位置选择行和列。
    df[df['column_name'] > value]	        选择列中满足条件的行。
    df.query('column_name > value')	        使用字符串表达式选择列中满足条件的行。

数据统计和描述
    df.describe()	计算基本统计信息，如均值、标准差、最小值、最大值等。
    df.mean()	    计算每列的平均值。
    df.median()	    计算每列的中位数。
    df.mode()	    计算每列的众数。
    df.count()	    计算每列非缺失值的数量。

"""


import pandas as pd


def series_test():
    """
    pandas.Series(data, index, dtype, name, copy) 类似表格中一列
    * data：一组数据(ndarray类型)。
    * index：数据索引标签，如果不指定，默认从0开始。
    * dtype：数据类型，默认会自己判断。
    * name：设置名称。
    * copy：拷贝数据，默认为False。
    """

    # 未指定索引值默认从0开始
    a = [1, 2, 3]
    myvar = pd.Series(a)
    # print(myvar)

    # 指定索引
    a = ["Google", "Runoob", "Wiki"]
    myvar = pd.Series(a, index=["x", "y", "z"])
    # print(myvar)

    # 使用key-value方式
    sites = {1: "Google", 2: "Runoob", 3: "Wiki"}
    myvar = pd.Series(sites)
    # 设置名称参数
    # myvar = pd.Series(sites, index=[1, 2], name="RUNOOB-Series-TEST")
    # print(myvar)


def dataFrame_test():
    """
    一个二维数组
    DataFrame 是一个表格型的数据结构，它含有一组有序的列，每列可以是不同的值类型（数值、字符串、布尔型值）
    DataFrame 既有行索引也有列索引，它可以被看做由 Series 组成的字典（共同用一个索引）
    pandas.DataFrame( data, index, columns, dtype, copy)
    * data：一组数据(ndarray、series, map, lists, dict 等类型)。
    * index：索引值，或者可以称为行标签。
    * columns：列标签，默认为 RangeIndex (0, 1, 2, …, n) 。
    * dtype：数据类型。
    * copy：拷贝数据，默认为 False。
    """

    # ndarrays
    mydataset = {
        'sites': ["Google", "Runoob", "Wiki"], # each column
        'number': [1, 2, 3],
    }
    myvar = pd.DataFrame(mydataset)
    # 设置索引
    myvar = pd.DataFrame(mydataset, index=["n1", "n2", "n3"])
    # print(myvar)
    # 使用loc返回指定行
    # print(myvar.loc[1])
    # 返回多行,返回结果就是一个 Pandas DataFrame
    # print(myvar.loc[[0, 1]])
    # loc返回指定索引
    # print(myvar.loc["n1"])

    # 列表
    data = [['Google', 10], ['Runoob', 12], ['Wiki', 13]]
    df = pd.DataFrame(data, columns=['Site', 'Age'])
    # print(df)

    # 字典
    data = [
        {'a': 1, 'b': 2}, # each row
        {'a': 5, 'b': 10, 'c': 20}
    ]
    df = pd.DataFrame(data)
    # print(df)


def csv_test():
    # 三个字段 name, site, age
    nm = ["Google", "Runoob", "Taobao", "Wiki"]
    st = ["www.google.com", "www.runoob.com", "www.taobao.com", "www.wikipedia.org"]
    ag = [90, 40, 80, 98]

    # 字典
    dict = {'name': nm, 'site': st, 'age': ag}

    # 保存 dataframe
    df = pd.DataFrame(dict)
    df.to_csv('site.csv')

    # print csv test
    df = pd.read_csv('XSS_dataset.csv')
    # print(df)
    # print(df.to_string())
    # to_string() 用于返回 DataFrame 类型的数据，
    # 如果不使用该函数，则输出结果为数据的前面 5 行和末尾 5 行，中间部分以 ... 代替

    # 读取前n行/后n行
    # print(df.head(3))
    # print(df.tail(3))

    # 返回基本信息
    print(df.info())


if __name__ == '__main__':
    print('————series_test————')
    series_test()
    print('————dataFrame_test————')
    dataFrame_test()
    print('————csv_test————')
    csv_test()
