'''
    1.先取出初始速度在df中的全部索引为列表a，如 a = [0, 1, 2, 4, 5, 9, 11, 12, 18]
    2.再取出终止速度在df中的全部索引为列表b,如 b = [6, 8, 14, 15, 17, 20, 22 ]
    3.通过算法得到初始（前）和结束（后）速度的索引列表c，如 c = [4, 6, 11, 14, 18, 20]
'''


import numpy as np
import pandas as pd
import warnings
import time
warnings.filterwarnings("ignore")





class accelerationCal:

    def __init__(self):
        self.mode = None
        self.filepath = None
        self.v_start = None
        self.v_end = None

    def menu(self):
        print("1. 加速稳定性")
        print("2. 加速响应时间一致性")
        print("3. ")
        print("4. ")
        choice = input("请输入你要进行的操作(1/2/3/4): ")
        return choice

    # 读取数据
    def readData(self):
        t1 = pd.read_csv(self.filepath, usecols=['Time','实时车速'],
                         encoding="gbk")
        t2 = t1.iloc[:, 0]
        t2_index = t2[t2.isin(['Time'])].index[0]  # 获取第二个TIME所在的行
        t3 = t1.iloc[:t2_index, :]
        t3 = t3.dropna(axis=0,how="any")
        return t3

    def findLeftBound(self,num, target):  # 查找到最后一个数都没有找到target，则left和right会交错，出现left>right，说明left为要找的数在该序列的上限索引
        left = 0
        right = len(num) - 1
        while (left <= right):
            mid = (left + right) // 2
            if num[mid] == target:
                return mid
            elif num[mid] > target:
                right = mid - 1
            else:
                left = mid + 1
        return left  # 要找的数在该序列的上限索引

    def recursion(self, t, va,zz,time):   #加速稳定性


        if (t[-1] - 500 < t[0]):
            return
        elif ((t[-1] - 500) in t):
            time.append((t[-1] + t[-1] - 500) / 2)
            zz.append((va[t.index(t[-1])] - va[t.index(t[-1] - 500)]) / 0.5)
            self.recursion(t[:-1], va,zz,time)
        else:
            time.append((t[-1] + t[-1] - 500) / 2)
            va_avg = (va[self.findLeftBound(t, t[-1] - 500)] + va[self.findLeftBound(t, t[-1] - 500) - 1]) / 2
            zz.append((va[t.index(t[-1])] - va_avg) / 0.5)
            self.recursion(t[:-1], va,zz,time)
            return zz,time


    def index_list(self):
        t3 = self.readData()
        a = [i for i in range(t3.shape[0]) if int(t3.iloc[i, 1]) == self.v_start] # 加速初始速度索引
        b = [i for i in range(t3.shape[0]) if int(t3.iloc[i, 1]) == self.v_end]  # 加速结束速度索引
        c = []
        print('v_start---', a)
        print('v_end---', b)
        i = len(b) - 1
        while (i != 0):  # i==0则退出循环，防止后面i-1数组越界
            while (b[i] == b[i - 1] + 1):
                b.pop(i)
                break
            i -= 1
        index_set = set()
        for i in range(len(b)):
            j = self.findLeftBound(a, b[i]) - 1
            while (a[j] == a[j - 1] + 1):
                j -= 1
            # print("初始速度的索引:\n",a[j])
            if a[j] not in index_set:
                c.append(a[j])
                c.append(b[i])
            index_set.add(a[j])

        # 速度必须单调才满足，截取的速度区间可能不单调[0,...,40,51,50]
        adjust = 0
        if (self.mode == 1):
            for i in range(0, len(c), 2):
                for j in range(c[i], c[i + 1]):
                    if (int(t3.iloc[j, 1]) > int(t3.iloc[j + 1, 1])):
                        p = i
                        adjust = 1
                        break
            if adjust:
                del c[p:p + 2]  # 前开后闭,放循环里会导致44行越界
        elif (self.mode == 3):
            for i in range(0, len(c), 2):
                for j in range(c[i], c[i + 1]):
                    if (int(t3.iloc[j, 1]) < int(t3.iloc[j + 1, 1])):
                        p = i
                        adjust = 1
                        break
            if adjust:
                del c[p:p + 2]  # 前开后闭,放循环里会导致44行越界

        return c


if __name__ == "__main__":
    # obj = accelerationCal("加速度",
    #                       r"C:\Users\lm\Desktop\test_data.csv",
    #                       0,
    #                       50)
    obj = accelerationCal()
    obj.filepath = str(input("请输入文件绝对路径: "))
    # std = obj.get_accStd()
    while True:
        choice = obj.menu()
        if choice == '1':
            obj.mode = 1
            obj.v_start = int(input("请输入初始速度(km/h): "))
            obj.v_end = int(input("请输入结束速度(km/h): "))
            t3 = obj.readData()
            c = obj.index_list()
            print("初始（前）和结束（后）速度的索引列表:",c)
            time_int = [int(i) for i in t3["Time"].values[c[0]:c[1] + 1]]
            v_int = [int(i) / 3.6 for i in t3["实时车速"].values[c[0]:c[1] + 1]]
            acc,time = obj.recursion(time_int, v_int,[],[])
            print("aaaa:\n", acc)
            print("tttt:\n", time)
            aj,time = obj.recursion(time[::-1], acc[::-1],[],[])
            print("加速度变化率:\n",aj)
        elif choice == '2':
            obj.mode = 1
            obj.v_start = int(input("请输入初始速度(0km/h): "))
            obj.v_end = int(input("请输入结束速度(30km/h): "))
            t3 = obj.readData()
            c = obj.index_list()
            print("初始（前）和结束（后）速度的索引列表:",c)
            gap_T = []
            for i in range(0, len(c), 2):
                gap_T.append(c[i+1] - c[i])
            T_index = np.std(gap_T)/np.mean(gap_T)
            print("加速响应相对标准偏差:\n",T_index)
        elif choice == '3':
            pass
        elif choice == '4':
            pass
        else:
            print("输入错误，请重新输入")

