import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import torch.optim as optim
import cv2
from sklearn.model_selection import train_test_split

# 导入csv
df = pd.read_csv("../test/XSS_dataset.csv", encoding="utf-8-sig")
sentences = df['Sentence'].values
# print(df.head(10))
# print(sentences[1])
# print(len(sentences))

def convert_to_ascii(sentence):
    sentence_ascii = []
    # print(len(sentence))

    for i in sentence:
        # 筛选出常见的字符
        # ord(i) 是内置函数调用,用于计算字符 i 的 ASCII 值
        if (ord(i) < 8222):
            if (ord(i) == 8217):  # ’  :  8217
                sentence_ascii.append(134)

            if (ord(i) == 8221):  # ”  :  8221
                sentence_ascii.append(129)

            if (ord(i) == 8220):  # “  :  8220
                sentence_ascii.append(130)

            if (ord(i) == 8216):  # ‘  :  8216
                sentence_ascii.append(131)

            if (ord(i) == 8217):  # ’  :  8217
                sentence_ascii.append(132)

            if (ord(i) == 8211):  # –  :  8211
                sentence_ascii.append(133)

            """
            If values less than 128 store them else discard them
            """
            if (ord(i) <= 128):
                sentence_ascii.append(ord(i))

            else:
                pass

    zer = np.zeros((10000)) #初始化一个长度为10000的向量

    for i in range(len(sentence_ascii)):
        zer[i] = sentence_ascii[i]
    # print(zer.shape)
    zer.shape = (100, 100) #将一维转为二维
    # print(zer.shape)

    #     plt.plot(image)
    #     plt.show()
    return zer