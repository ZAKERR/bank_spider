# -*- coding: utf-8 -*-
import re


def get_cf_yj(txt):
    """ 获取处罚依据 """
    if txt:
        first = re.compile(r'((根据|依据|违反).*?第.*?(规定|条))')
        first = first.search(txt)
        second = re.search(r'((违反|根据|依据).*?。)', txt)
        if first:
            cf_yj = first.group()
        elif second:
            cf_yj = second.group()
        else:
            cf_yj = ''
        return cf_yj
    return ''


def get_cf_sy(txt):
    """ 获取处罚事由 """
    if txt:
        first = re.compile(r'(指其.*?。)')
        first = first.search(txt)
        first_one = re.search(r'((查讯后发现|证监会对事件进行调查后|证监会就).*?。)', txt)
        second = re.compile(r'(宣布，|公布，)(.*?。)')
        second = second.search(txt)
        third = re.compile(r'(：)(.*?。)')
        third = third.search(txt)
        fourth = re.search(r'(日)(证监会.*?。)', txt)
        if first:
            cf_sy = first.group()
        elif first_one:
            cf_sy = first_one.group()
        elif second:
            cf_sy = second.group(2)
        elif third:
            cf_sy = third.group(2)
        elif fourth:
            cf_sy = fourth.group(2)
        else:
            cf_sy = ''
        return cf_sy
    else:
        return ''


def get_cf_jg(txt):
    """ 获取处罚结果 """
    if txt:
        first = re.compile(r'(罚款.*?。)')
        first = first.search(txt)
        second = re.compile(r'(宣布，|公布，|决定)(.*?。)')
        second = second.search(txt)
        third = re.search(r'(日)(证监会.*?。)', txt)
        if first:
            cf_jg = first.group()
        elif second:
            cf_jg = second.group(2)
        elif third:
            cf_jg = third.group(2)
        else:
            cf_jg = ''
        return cf_jg
    return ''


if __name__ == '__main__':
    txt = '证监会暂时吊销朱景球的注册资格1997年9月4日证监会今天宣布，暂时吊销朱景球（朱氏）作为以大盛证券投资公司（大盛）名义营业的陈婉仪的证券交易商代表资格，由1997年8月25日起生效，为期2年。证监会就朱氏于1993年10月至1994年1月期间的交易展开调查，发现朱氏期内曾透过大盛一个代名人账户，以不正当的方式进行买卖，从而以最佳价格获分配股份，从中图利总共237,165元，导致大盛的客户利益受损。结果该会便采取这次行动。朱氏又曾参与沽空证券的活动，而法院亦就此于1997年2月25日裁定他违反《证券条例》第80条。此外，证监会发现朱氏曾在明知的情况下，协助大盛一名客户从事沽空证券活动。朱氏的行为实有损投资大众的利益。证监会发言人表示，这宗暂时吊销注册资格的个案，显示证监会继续致力惩治该等以不正当方式进行买卖、危害投资大众利益的注册人士。为了确保注册中介团体持正操作，证监会将会对违规的注册人士，采取严厉的监管行动。如有任何查询，请致电(2840-9287)与韦克志或陈志强联络。最后更新日期:2012年8月1日证监会暂时吊销罗菊珍的牌照1997年12月18日证监会今天宣布，该会已暂时吊销罗菊珍（罗氏）的槓杆式外汇买卖商代表的牌照，由1997年12月15日起生效，为期一年。证监会作出此项行动，是由于罗氏在受僱于南贵金融（香港）有限公司为持牌槓杆式外汇买卖商代表期间，以一家以澳门为基地的景生金融服务有限公司（景生）的代理人的身份，向他人显示其无牌经营槓杆式外汇买卖业务。罗氏亦因此在1997年8月28日于西区裁判法院被控违反《槓杆式外汇买卖条例》（该条例），罪名成立，被判罚款50,000元。证监会发言人就罗氏作出的行动表示："证监会必定会采取严厉的措施，阻止任何持牌买卖商代表违反该条例的规定，而令投资者丧失该条例所提供的保障。证监会希望这项对罗氏的检控及处分，会对其他人起着阻吓作用。"如有任何查询，请致电(2840-9287)与韦克志或陈志强联络。最后更新日期:2012年8月1日'
    cf_yj = get_cf_yj(txt)
    print(f'处罚依据:{cf_yj}')
    cf_sy = get_cf_sy(txt)
    print(f'处罚事由:{cf_sy}')
    cf_jg = get_cf_jg(txt)
    print(f'处罚结果:{cf_jg}')