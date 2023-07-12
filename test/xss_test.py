import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import torch.optim as optim
import cv2
from sklearn.model_selection import train_test_split

# 导入csv
df = pd.read_csv("XSS_dataset.csv",encoding="utf-8-sig")
sentences = df['Sentence'].values
# print(df.head(10))
# print(sentences[1])
# print(len(sentences))

