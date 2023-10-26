# -- coding: utf-8 --

# @File : utils.py
# @Time : 2023/4/19 15:37
# @Author : windyzhao

def split_list(_list, count=100):
    n = len(_list)
    sublists = [_list[i: i + count] for i in range(0, n, count)]
    return sublists
