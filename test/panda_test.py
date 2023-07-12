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
    df = pd.read_csv('nba.csv')
    print(df.to_string())


if __name__ == '__main__':
    # print('————series_test————')
    # series_test()
    # print('————dataFrame_test————')
    # dataFrame_test()
    print('————csv_test————')
    csv_test()
