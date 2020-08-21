#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Date          : 2020/3/6
@Author        : wangtao35@baidu.com
@File          : reminder.py
@Description   : 本脚本只考虑买入，每日跌幅/基准 放大，与上证指数强挂钩， 初版算法，结合实践不断迭代优化
                    卖出需认为干预，目标跑赢沪深300，年化15
                    买入固定值，卖出百分比
                    也许以后可以出售本工具服务，嘻嘻
"""
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import requests
import logging
import smtplib
import time
import re
import json
from email.header import Header
from email.mime.text import MIMEText

logging.basicConfig(filename='fund_sentinel.log', format='%(asctime)s:%(levelname)s:%(message)s', level=logging.INFO)

header = {"User-Agent": UserAgent().chrome}

mail_host = "smtp.163.com"  # SMTP服务器
mail_user = "13786166582@163.com"
mail_pass = "wangTAO321"
sender = "13786166582@163.com"
receivers = ["13786166582@163.com"]
title = '基金哨兵'


def fund_spider(id, name, rise_threshold, decline_threshold, base, confidence, correlation):
    sz_url = 'https://xueqiu.com/S/SH000001'
    sz_html = requests.get(sz_url, headers=header).text
    url = 'http://fund.eastmoney.com/{}.html'.format(id)
    res_html = requests.get(url, headers=header).text
    try:
        sz_bs = BeautifulSoup(sz_html, 'lxml')
        index_value = float(sz_bs.select('.stock-current > strong')[0].string)  # 上证指数
        # print(index_value)

        bs = BeautifulSoup(res_html, 'lxml')
        # select_list = bs.select('#gz_gszzl')  # list
        # change = float(select_list[0].string.split('%')[0])  # 预估涨跌幅
        now_timestamp = int(time.time()) * 1000
        res = requests.get('http://fundgz.1234567.com.cn/js/{}.js?rt={}'.format(id, now_timestamp)).text
        res = re.search('\{.*\}', res).group()
        # print(res)
        change = float(json.loads(res)['gsz'])  # 预估涨跌幅

        select_list = bs.select('.dataNums')
        # print(select_list[-1].find('span').string)
        value = float(select_list[-1].find('span').string)  # 净值
    except Exception as e:
        msg = 'bs parse error: {}\n'.format(e)
        logging.error(msg)
        return msg
    if change > rise_threshold:
        msg = ' <h2>{} : {}/今日估算净值{}, <b style="color:red">{}%</b> ' \
              '涨幅超过 <b style="color:red">{}%</b> , 可以考虑分批卖出 </h2>'.\
            format(id, name, value, change, rise_threshold)
        return msg
    if change < -decline_threshold:
        # 2780代表基准，市场越乐观该值越大
        # 800代表震荡幅度，预估震荡幅度越大该值越大买入越谨慎
        to_buy = int((100 * (change / -decline_threshold) ** 1 + base) *
                     confidence *
                     (1 + (2780 - index_value) / 800 * correlation) ** 4)
        msg = ' <h2>{} : {}/今日估算净值{}, <b style="color:green">{}%</b> ' \
              '跌幅超过 <b style="color:green">{}%</b> , 可以考虑买入 {} </h2>'.\
            format(id, name, value, change, decline_threshold, to_buy)
        return msg
    return ''


def send_mail(msg):
    message = MIMEText(msg, 'html', 'utf-8')  # 内容, 格式, 编码
    message['From'] = "{}".format(sender)
    message['To'] = ",".join(receivers)
    message['Subject'] = title

    try:
        smtpObj = smtplib.SMTP_SSL(mail_host, 465)  # 启用SSL发信, 端口一般是465
        smtpObj.login(mail_user, mail_pass)  # 登录验证
        smtpObj.sendmail(sender, receivers, message.as_string())  # 发送
        logging.info("mail has been send successfully.")
    except smtplib.SMTPException as e:
        logging.error(e)


def main():
    # 基金字典列表 id、name、涨幅通告阈值、跌幅通告阈值、信心指数（0-1）、基础金
    # todo 1.上证指数关联度 2.信心指数判断涨幅通告阈值，大于等于0.7即使用99分位，否则90分位历史涨幅值
    fund_list = [
        {
            'id': '110003',
            'name': '易方达上证50指数A',
            'rise_threshold': 2.75,
            'decline_threshold': 1.65,
            'confidence': 0.9,
            'correlation': 1,
            'base': 500,
        },
        {
            'id': '530015',
            'name': '建信深证基本面60ETF联接A',
            'rise_threshold': 2.34,
            'decline_threshold': 1.49,
            'confidence': 0.77,
            'correlation': 0.95,
            'base': 400,
        },
        {
            'id': '161017',
            'name': '富国中证500指数(LOF)',
            'rise_threshold': 2.33,
            'decline_threshold': 1.66,
            'confidence': 0.8,
            'correlation': 0.9,
            'base': 400,
        },
        {
            'id': '163411',
            'name': '兴全精选混合',
            'rise_threshold': 1.56,
            'decline_threshold': 0.78,
            'confidence': 0.7,
            'correlation': 0.8,
            'base': 400,
        },
        {
            'id': '161725',
            'name': '招商中证白酒指数分级',
            'rise_threshold': 2.61,
            'decline_threshold': 2.14,
            'confidence': 0.6,
            'correlation': 0.6,
            'base': 300,
        },
        {
            'id': '110022',
            'name': '易方达消费行业股票',
            'rise_threshold': 2.29,
            'decline_threshold': 1.49,
            'confidence': 0.7,
            'correlation': 0.8,
            'base': 200,
        },
        {
            'id': '008087',
            'name': '华夏中证5G通信主题ETF联接C',
            'rise_threshold': 3.6,
            'decline_threshold': 2.84,
            'confidence': 0.7,
            'correlation': 0.4,
            'base': 400,
        },
        {
            'id': '008903',
            'name': '广发科技先锋混合',
            'rise_threshold': 3.6,
            'decline_threshold': 2.84,
            'confidence': 0.6,
            'correlation': 0.4,
            'base': 300,
        },
        {
            'id': '007203',
            'name': '银河新动能混合',
            'rise_threshold': 3.6,
            'decline_threshold': 2.84,
            'confidence': 0.5,
            'correlation': 0.4,
            'base': 300,
        },
        {
            'id': '001373',
            'name': '易方达新丝路灵活配置混合',
            'rise_threshold': 2.6,
            'decline_threshold': 1.7,
            'confidence': 0.6,
            'correlation': 0.7,
            'base': 300,
        },
        {
            'id': '005827',
            'name': '易方达蓝筹精选混合',
            'rise_threshold': 2.32,
            'decline_threshold': 1.56,
            'confidence': 0.8,
            'correlation': 0.8,
            'base': 500,
        },
        {
            'id': '519736',
            'name': '交银新成长混合',
            'rise_threshold': 2.72,
            'decline_threshold': 1.54,
            'confidence': 0.6,
            'correlation': 0.7,
            'base': 400,
        },
        {
            'id': '519712',
            'name': '交银阿尔法核心混合',
            'rise_threshold': 2.45,
            'decline_threshold': 1.41,
            'confidence': 0.6,
            'correlation': 0.6,
            'base': 300,
        },
        {
            'id': '519066',
            'name': '汇添富蓝筹稳健混合',
            'rise_threshold': 2.16,
            'decline_threshold': 1.36,
            'confidence': 0.7,
            'correlation': 0.5,
            'base': 400,
        },
        {
            'id': '007412',
            'name': '景顺长城绩优成长混合',
            'rise_threshold': 2.68,
            'decline_threshold': 1.45,
            'confidence': 0.7,
            'correlation': 0.4,
            'base': 500,
        },
        {
            'id': '001071',
            'name': '华安媒体互联网混合',
            'rise_threshold': 3.48,
            'decline_threshold': 2.11,
            'confidence': 0.6,
            'correlation': 0.4,
            'base': 400,
        },
        {
            'id': '005729',
            'name': '南方人工智能混合',
            'rise_threshold': 2.52,
            'decline_threshold': 1.42,
            'confidence': 0.6,
            'correlation': 0.3,
            'base': 300,
        },
        {
            'id': '004424',
            'name': '汇添富文体娱乐主题混合',
            'rise_threshold': 2.41,
            'decline_threshold': 1.17,
            'confidence': 0.6,
            'correlation': 0.5,
            'base': 400,
        },
        {
            'id': '006007',
            'name': '诺安积极配置混合A',
            'rise_threshold': 2.28,
            'decline_threshold': 1.1,
            'confidence': 0.7,
            'correlation': 0.6,
            'base': 400,
        },
        {
            'id': '320012',
            'name': '诺安主题精选混合',
            'rise_threshold': 2.1,
            'decline_threshold': 1.38,
            'confidence': 0.7,
            'correlation': 0.6,
            'base': 400,
        },
        {
            'id': '000751',
            'name': '嘉实新兴产业股票',
            'rise_threshold': 4.14,
            'decline_threshold': 0.91,
            'confidence': 0.7,
            'correlation': 0.2,
            'base': 500,
        },
        {
            'id': '001679',
            'name': '前海开源中国稀缺资产灵活配置A',
            'rise_threshold': 4.36,
            'decline_threshold': 0.5,
            'confidence': 0.8,
            'correlation': 0.4,
            'base': 500,
        },
    ]

    sum_msg = ''
    for fund in fund_list:
        sum_msg += fund_spider(fund['id'],
                               fund['name'],
                               fund['rise_threshold'],
                               fund['decline_threshold'],
                               fund['base'],
                               fund['confidence'],
                               fund['correlation']) + '\n'
    send_mail(sum_msg)


if __name__ == '__main__':
    main()

