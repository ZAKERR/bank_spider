# -*- coding: utf-8 -*-
from nstools.langconv import *


def TraditionalToSimplified(line):
    """ 繁体转简体 """
    line=Converter("zh-hans").convert(line)
    return line


def SimplifiedToTraditional(line):
    """ 简体转繁体 """
    line=Converter("zh-hant").convert(line)
    return line


if __name__ == "__main__":
    line="證券及期貨事務監察委員會"
    line=SimplifiedToTraditional(line)
    print(f'繁体:{line}')
    line=TraditionalToSimplified(line)
    print(f'简体:{line}')