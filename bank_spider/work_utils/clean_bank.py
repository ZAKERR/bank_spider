# -*- coding: utf-8 -*-
import re


def get_oname(txt):
    """ 获取处罚主体 """
    if txt:
        head = re.search(r'(受处罚人姓名：)(.*?)(年龄)', txt)
        first = re.search(r'(个人姓名：|单位名称：|当事人:|当事人：|被处罚个人名称：|处罚人：|受处罚机构：|受罚人（机构）：|受处罚机构名称：|受处罚人名称：|受处罚人姓名：)(.*?公司.*?(支|分)公司)(年龄|Microsoft|银监会|身份证|营业|地址|住址|住所|职务|主要负责人)', txt)
        second = re.search(r'(个人姓名：|单位名称：|当事人:|当事人：|被处罚个人名称：|处罚人：|受处罚机构：|受罚人（机构）：|受处罚机构名称：|受处罚人名称：|受处罚人姓名：)(.*?)(Microsoft|银监会|身份证|营业|地址|住址|住所|年龄|职务|主要负责人|\d+岁|，)', txt)
        third = re.search(r'(被处罚机构：|告知书|被处罚人姓名：|经查，|当事人一：)(.*?公司.*?(支|分)公司)(年龄|Microsoft|银监会|身份证|营业|地址|住址|住所|职务|主要负责人|存在)', txt)
        fourth = re.search(r'(被处罚人姓名：)(.*?)(：|住址)', txt)
        five = re.search(r'(.*?)(：)', txt)
        if head:
            oname = head.group(2)
        elif first:
            oname = first.group(2)
        elif second:
            oname = second.group(2)
        elif third:
            oname = third.group(2)
        elif fourth:
            oname = fourth.group(2)
        elif five:
            oname = five.group(1)
        else:
            oname = ''
        return oname
    return ''


def get_cf_wsh(txt):
    """ 获取处罚文书号 """
    if txt:
        head = re.search(r'(闽保监.*?\d{4}.*?\d+.*?号)', txt)
        first = re.search(r'[\(（ ](.*?罚.*?\d{4}.*?\d+号)', txt)
        second = re.search(r'(行政处罚决定书.*?\d{4}.*?\d+号)', txt)
        third = re.search(r'(.*?保监罚\d{4}.*?\d+.*?号)', txt)
        four = re.search(r'(.*?保监罚.*?\d{4}.*?\d+.*?号)', txt)
        if head:
            wsh = head.group(1)
        elif first:
            wsh = first.group(1)
        elif second:
            wsh = second.group(1)
        elif third:
            wsh = third.group(1)
        elif four:
            wsh = four.group(1)
        else:
            wsh = ''
        return wsh
    else:
        return ''


def get_cf_yj(txt):
    """ 获取处罚依据 """
    if txt:
        first = re.search(r'((根据|依据|违反了).*?第.*?(条|规定))', txt)
        if first:
            cf_yj = first.group()
        else:
            cf_yj = ''
        return cf_yj
    return ''


def get_cf_sy(txt):
    """ 获取处罚事由 """
    if txt:
        first = re.search(r'(存在以下违法行为：|存在下列违法行为：|违法行为：|经查，|存在以下违法违规行为：|存在下列违规行为：)(.*?)(上述事实|我会决定作出如下处罚|经复核|上述行为违反了|依据.*?第.*?规定|依据《|以上行为)', txt)
        second = re.search(r'(我局.*?检查.*?发现.*?。)', txt)
        if first:
            cf_sy = first.group(2)
        elif second:
            cf_sy = second.group(1)
        else:
            cf_sy = ''
        return cf_sy
    else:
        return ''


def get_cf_jg(txt):
    """ 获取处罚结果 """
    if txt:
        first = re.search(r'(作出如下处罚：|决定给予你单位以下行政处罚：|条规定，)(.*?)(当事人如对本处罚决定不服|如你公司|请在接到本处罚决定书)', txt)
        second = re.search(r'((现责令|决定给予|我局决定|对你公司).*?。)', txt)
        if first:
            cf_jg = first.group(2)
        elif second:
            cf_jg = second.group(1)
        else:
            cf_jg = ''
        return cf_jg
    return ''


def get_cf_jdrq(txt):
    """ 获取处罚决定日期 """
    if txt:
        first = re.search(r'(二○.*?年.*?月.*?日)', txt)
        second = re.search(r'(二\d+.*?年.*?月.*?日)', txt)
        third = re.search(r'(二О.*?年.*?月.*?日)', txt)
        fourth = re.search(r'(二〇.*?年.*?月.*?日)', txt)
        five = re.search(r'(二O.*?年.*?月.*?日)', txt)
        six = re.search(r'(\d{4}年\d+月\d+日)', txt)

        if first:
            cf_jdrq = first.group(1)
        elif second:
            cf_jdrq = second.group(1)
        elif third:
            cf_jdrq = third.group(1)
        elif fourth:
            cf_jdrq = fourth.group(1)
        elif five:
            cf_jdrq = five.group(1)
        elif six:
            cf_jdrq = six.group(1)
        else:
            cf_jdrq = None
        return cf_jdrq
    else:
        return None


def handles_cf_jdrq(cf_jdrq):
    """ 汉字的日期转数字日期 """
    if cf_jdrq:
        mapper = {"〇": "0", "一": "1", "二": "2", "三": "3", "四": "4", "五": "5", "六": "6", "七": "7", "八": "8",
                  "九": "9", "年": "-", "月": "-", "日": "-", "○": "0", "О": "0", "O": "0"}

        # 替换年月日，及1-9汉字
        new_jdrq = ""
        for word in cf_jdrq:
            if word in mapper.keys():
                new_jdrq += mapper[word]
            else:
                new_jdrq += word

        # 处理十，分几种情况，1.在最左边，在中间，在最后边
        cf_jdrq = ""
        digit_list = [str(digit) for digit in range(1, 10)]
        for idx, word in enumerate(new_jdrq):
            if word == "十":
                # 最左边
                if new_jdrq[idx - 1] == '-' and new_jdrq[idx + 1] in digit_list:
                    cf_jdrq += "1"
                elif new_jdrq[idx - 1] == "-" and new_jdrq[idx + 1] not in digit_list:
                    cf_jdrq += "10"
                elif new_jdrq[idx - 1] in digit_list and new_jdrq[idx + 1] in digit_list:
                    cf_jdrq += ""
                else:
                    cf_jdrq += "0"
            else:
                cf_jdrq += word
        return cf_jdrq[:-1]
    else:
        return None


if __name__ == '__main__':
    txt = '苏银保监罚决字〔2019〕64号被处罚人姓名：陈跃飞住址：南京市建邺区集庆门大街219号身份证号：32068319821024****依据《中华人民共和国保险法》《中华人民共和国行政处罚法》等有关法律规定，我局对中国平安财产保险股份有限公司宿迁中心支公司（以下简称平安财险宿迁中支）财务数据不真实一案进行了调查、审理，并依法向当事人告知了作出行政处罚的事实、理由、依据以及当事人依法享有的权利。在法定陈述申辩期内，当事人未提出陈述申辩意见。本案现已审理终结。2018年9-12月，平安财险宿迁中支通过服务费、宣传费两个科目列支费用7480351元，实为公司给予业务部门保费金额3%-40%的销售费用，用于支付车商和其他代理机构超过手续费上限的额外费用。相关服务费、宣传费事项实际并未发生。陈跃飞时任平安财险宿迁中支总经理，任职期间同意了公司虚列费用的行为，导致公司财务数据不真实，应认定为直接负责的主管人员。上述事实，有现场检查事实确认书、公司车险业务情况说明及其附件、公司费用列支的签报及报销凭证、案涉承保清单及超手续费上限的跟单补贴费用明细、相关人员调查笔录、任职分工文件等证据证明。综上，我局决定作出如下处罚：上述财务数据不真实的行为，违反了《中华人民共和国保险法》第八十六条第二款的规定，根据《中华人民共和国保险法》第一百七十一条的规定，给予陈跃飞警告，并处8万元罚款。当事人应当在接到本处罚决定书之日起15日内持缴款码（缴款码将在处罚决定书送达时告知）到财政部指定的12家代理银行中的任一银行进行同行缴款。逾期，将每日按罚款数额的3%加处罚款。当事人如对本处罚决定不服，可在收到本处罚决定书之日起60日内向中国银行保险监督管理委员会申请行政复议，也可在收到本处罚决定书之日起6个月内直接向有管辖权的人民法院提起行政诉讼。复议和诉讼期间，上述决定不停止执行。中国银保监会江苏监管局2019年12月19日'
    oname = get_oname(txt)
    print(f'主体:{oname}')
    cf_wsh = get_cf_wsh(txt)
    print(f'文书号:{cf_wsh}')
    cf_yj = get_cf_yj(txt)
    print(f'处罚依据:{cf_yj}')
    cf_sy = get_cf_sy(txt)
    print(f'处罚事由:{cf_sy}')
    cf_jg = get_cf_jg(txt)
    print(f'处罚结果:{cf_jg}')
    cf_jdrq = get_cf_jdrq(txt)
    print(f'处罚决定日期:{cf_jdrq}')
    cf_rq = handles_cf_jdrq(cf_jdrq)
    print(f'处理完成的日期:{cf_rq}')