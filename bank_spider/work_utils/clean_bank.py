# -*- coding: utf-8 -*-
import re


def get_oname(txt):
    """ 获取处罚主体 """
    if txt:
        oname_com = re.compile(r'(单位名称：|当事人:|当事人：|：)(.*?)(身份证号|营业地址|地址)')
        oname = oname_com.search(txt)
        oname = oname.group(2) if oname else ''
        return oname
    return ''


def get_cf_wsh(txt):
    """ 获取处罚文书号 """
    if txt:
        wsh_com = re.compile(r'(.*?(罚|告).*?(\(|〔|（).*?\d{4}.*?\d+号)')
        cf_wsh = wsh_com.search(txt)
        cf_wsh = cf_wsh.group() if cf_wsh else ''
        return cf_wsh
    return ''


def get_cf_yj(txt):
    """ 获取处罚依据 """
    if txt:
        yj_com = re.compile(r'((根据|依据|违反了).*?(规定|条))')
        cf_yj = yj_com.search(txt)
        cf_yj = cf_yj.group() if cf_yj else ''
        return cf_yj
    return ''


def get_cf_sy(txt):
    """ 获取处罚事由 """
    if txt:
        sy_com = re.compile(r'(存在以下违法行为：|存在下列违法行为：|违法行为：|经查，)(.*?。)')
        cf_sy = sy_com.search(txt)
        cf_sy = cf_sy.group(2) if cf_sy else ''
        return cf_sy
    else:
        return ''


def get_cf_jg(txt):
    """ 获取处罚结果 """
    if txt:
        jg_com = re.compile(r'((现对|我局决定).*?。)')
        cf_jg = jg_com.search(txt)
        cf_jg = cf_jg.group() if cf_jg else ''
        return cf_jg
    return ''
