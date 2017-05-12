# -*- coding: utf-8 -*-
from operator import itemgetter
import urllib2
import urllib
import re
from bs4 import BeautifulSoup
import os
import sys
import jieba.posseg as pseg
import jieba
import numpy as np
import jieba.posseg as pseg
reload(sys)
sys.setdefaultencoding("utf-8")

jieba.load_userdict(os.getcwd()+'\\dictionary\\emotion_dict\\user_dict.txt')

# 切分sentence为单词
def segmentation(sentence):
    seg_list = jieba.cut(sentence)
    result = []
    for word in seg_list:
        result.append(word)
    return result


def psegCut(content):
    content = content.decode('utf8')
    label = ['a', 'v', 'n', 'vn', 'ag', 'vi']
    words = pseg.cut(content)
    result = []
    for w in words:
        if w.flag in label:
            result.append(w.word)
    return result


# 根据句中标点切分句子，除去句中标点符号,并断句
def cut_sentence(words):
    words = words.decode('utf8')
    start = 0
    i = 0
    result = []
    punt_list = ',.!?;~，、。！:？""；～… ()<>'.decode('utf8')
    #punt_list = ',.!?;。！:？""；…'.decode('utf8')
    for word in words:
        # print "word",word
        if word not in punt_list:       # 如果不是标点符号
            i += 1
        else:
            # print "word3", word
            if start == i:              # 如果是连续的标点符号
                start = i + 1
                i += 1
                continue
            result.append(words[start:i])  # 断句，并保存
            start = i + 1
            i += 1
    if start < len(words):  # 处理最后可能不含标点的部分
            result.append(words[start:])
    return result


def loadDict(filename):
    file = open(os.getcwd() + filename, 'r')
    words_dict = []
    for line in file.readlines():
        line = line.decode('utf-8').split('\t')
        words_dict.append((line[0], float(line[1])))
    file.close()
    return words_dict


def read_file(filename):
    file = open(os.getcwd() + filename, 'r')
    dict = []
    for line in file.readlines():
        line = line.strip()
        line = line.decode('utf-8')
        dict.append(line)
    file.close()
    return dict


def write_file(filename, content_dict):
    file = open(os.getcwd() + filename, 'w')
    for content in content_dict:
        file.write(content)
        file.write('\n')
    file.close()


if __name__ == '__main__':
    # content_list = read_file('\\dictionary\\testData_new.txt')
    # length = len(content_list[0])
    # print content_list[0][:length/2]
    a = '我是中国人。你们'
    b = jieba.cut(a.decode('utf-8'))
    c = pseg.cut(a.decode('utf-8'))
    for i in b:
        print i
    print '------------------'
    for i in c:
        print i.word, i.flag