from pypinyin import lazy_pinyin
import re


def to_pinyin(ch_name):
    """
    将混合转化为搜索拼音字符
    INPUT '杭州frank1湖滨银泰in77'
    OUTPUT 'hzfrank1hbytin77'
    """
    print('to_pinyin -->  ',ch_name)
    d1 = re.sub(r'[a-zA-Z0-9]+',' ',ch_name)
    d2 = re.findall(r'[a-zA-Z0-9]+',ch_name)
    d3 = lazy_pinyin(d1)
    d4 = []
    i=0
    for d in d3:
        if d == ' ':
            d4.append(d2[i])
            i+=1
        else:
            d4.append(d[0])
    d4 = ''.join(d4)
    return d4

'''
log
'''
import logging
logging.basicConfig(
    format = '%(asctime)s %(levelname)-4s %(message)s',
    level=logging.INFO,
    datefmt='%d %H:%M:%S')
