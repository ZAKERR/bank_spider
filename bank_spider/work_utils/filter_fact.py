# -*- coding: utf-8 -*-
import hashlib
import re


def get_md5_value(_str):
    if isinstance(_str, str):
        md5_obj = hashlib.md5()
        md5_obj.update(_str.encode())
        md5_code = md5_obj.hexdigest()
        return md5_code
    else:
        return None


def deal_with_cf_wsh(cf_wsh):
    if cf_wsh:
        cf_wsh = re.sub(r'\r|\?|\n|\t| |　', '', cf_wsh)
        cf_wsh = re.sub(r'〔|\[|【|（|﹝|{　', '(', cf_wsh)
        cf_wsh = re.sub(r'〕|]|】|）|﹞|}', ')', cf_wsh)
        return cf_wsh
    else:
        return ""


def deal_with_other(_str):
    if _str:
        _str = re.sub(r'\r|\?|\n|\t| |　', '', str(_str))
        return _str
    else:
        return ""


def cf_43_filter(item):
    """ 银保监去重规则 """
    if isinstance(item, dict):
        xq_url = item.get("xq_url", '')
        oname = item.get('oname', '')  # 主体
        oname = deal_with_other(oname)
        cf_jdrq = item.get('cf_jdrq', '')  # 处罚决定日期
        cf_wsh = item.get('cf_wsh', '')  # 处罚文书号
        cf_wsh = deal_with_cf_wsh(cf_wsh)

        if xq_url:
            if oname:
                if cf_jdrq:
                    if cf_wsh:
                        _str = str(xq_url) + oname + cf_jdrq + cf_wsh
                        return get_md5_value(_str)
                    else:
                        _str = str(xq_url) + oname + cf_jdrq
                        return get_md5_value(_str)
                else:
                    _str = xq_url + oname
                    return get_md5_value(_str)
            else:
                _str = xq_url
                return get_md5_value(_str)
        else:
            return None


def cf_15_filter(item):
    """ 香港证监会清洗规则 """
    if isinstance(item, dict):
        xq_url = item.get("xq_url", '')
        oname = item.get('oname', '')  # 主体
        oname = deal_with_other(oname)
        cf_jdrq = item.get('cf_jdrq', '')  # 处罚决定日期
        cf_cfmc = item.get('cf_cfmc', '')

        if xq_url:
            if cf_cfmc:
                if cf_jdrq:
                    if oname:
                        _str = xq_url + cf_cfmc + cf_jdrq + oname
                        return get_md5_value(_str)
                    else:
                        _str = xq_url + cf_cfmc + cf_jdrq
                        return get_md5_value(_str)
                else:
                    _str = xq_url + cf_cfmc
                    return get_md5_value(_str)
            else:
                _str = xq_url
                return get_md5_value(_str)
        else:
            return None


def cf_10_filter(item):
    """ 北京市税务局重大涉税 """
    if isinstance(item, dict):
        oname = item.get('oname', '')
        uccode = item.get('uccode', '')
        cf_cfmc = item.get('cf_cfmc', '')
        etcode = item.get('etcode', '')
        cf_r_id = item.get('cf_r_id', '')
        if oname:
            if uccode:
                if cf_cfmc:
                    if cf_r_id:
                        if etcode:
                            _str = oname + uccode + cf_cfmc + cf_r_id + etcode
                            return get_md5_value(_str)
                        else:
                            _str = oname + uccode + cf_cfmc + cf_r_id
                            return get_md5_value(_str)
                    else:
                        _str = oname + uccode + cf_cfmc
                        return get_md5_value(_str)
                else:
                    _str = oname + uccode
                    return get_md5_value(_str)
            else:
                _str = oname
                return get_md5_value(_str)
        else:
            return None


def cf_filter_fact(item):
    sj_type = item.get('sj_type')
    if sj_type == '43':
        return cf_43_filter(item)
    elif sj_type == '15':
        return cf_15_filter(item)
    elif sj_type == '10':
        return cf_10_filter(item)
    else:
        print('未定义去重规则')