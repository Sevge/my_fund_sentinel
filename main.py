#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Date          : 2020/3/6
@Author        : wangtao35@baidu.com
@File          : main.py
@Description   : 
"""
import csv


def to_int(s):
    if '%' in s:
        return float(s.split('%')[0])
    else:
        return 0


def stock(month_std=3, tree_month_std=5, half_year_std=10, one_year_std=5, tree_year_std=25):
    # 股票筛选规则
    new = []
    one_year = []
    tree_year = []
    f = csv.reader(open('all/股票指数.csv', 'r'))
    flag = 1
    for i in f:
        # 过滤第一行，即表头
        if flag == 1:
            flag = 0
            continue
        # 过滤资金规模过小的
        # if float(i[2].split('亿')[0]) < 1 or i[2] == '--':
        #     continue

        if to_int(i[3]) == 0:
            new.append(i)

        if to_int(i[7]) == 0:
            if to_int(i[6]) != 0:
                if to_int(i[6]) / to_int(i[5]) > 2 and to_int(i[3]) < month_std:
                    one_year.append(i)
        else:
            if to_int(i[7]) / to_int(i[6]) > 3 and to_int(i[7]) > tree_year_std and to_int(i[3]) < month_std:
                tree_year.append(i)

    print(len(new), 'new:')
    for i in new: print(i)
    print(len(one_year), 'new one year:')
    for i in one_year: print(i)
    print(len(tree_year), 'tree_year:')
    for i in tree_year: print(i)


def bond():
    # 债券排序
    f = list(csv.reader(open('all/债券型.csv', 'r')))
    struct_list = []
    # 将数据格式化为int，方便排序
    flag = 0
    for i in f:
        if flag == 0:
            flag = 1
            continue
        for j in range(3, 9):
            i[j] = to_int(i[j])
        struct_list.append(i)

    # 根据某个key排序，3-近1月，4-近3月，5-近6月，6-近一年，7-近3年
    k = 6
    sorted_list = sorted(struct_list, key=lambda x: x[k])
    for i in sorted_list:
        # 抖动过大的过滤
        if i[6] != 0 and i[5] != 0:
            tmp = i[7] / i[6]
            tmp2 = i[6] / i[5]
            if tmp > 3.8 or tmp < 2.5:
                continue
            if tmp2 > 2.7 or tmp2 < 1.5:
                continue
            print(i)
        else:
            print(i)


def analysis():
    f = csv.reader(open('detail/005729.csv', 'r'))
    flag = 1
    changes_list = []
    for i in f:
        if flag == 1:
            flag = 0
            continue
        if i[4]:
            changes_list.append(float(i[4].split('%')[0]))

    changes_list.sort()
    percent = [1/20, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99]
    for p in percent:
        index = int(len(changes_list)*p)
        print('{}: {}'.format(p, changes_list[index]))


if __name__ == '__main__':
    # bond()
    # stock()
    analysis()


