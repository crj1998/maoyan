# -*- coding: utf-8 -*-
# @Author: Chen Renjie
# @Date:   2019-02-11 14:56:07
# @Last Modified by:   Chen Renjie
# @Last Modified time: 2019-02-12 14:46:24

import requests
import lxml.etree
import re

from fonts import parse_font, convert

url = "https://piaofang.maoyan.com/rankings/year"
r=requests.get(url)
html=lxml.etree.HTML(r.text)
fontUrl = re.search(re.compile(r'url\(.+?\)'), html.xpath("//style[@id='js-nuwa']/text()")[0])
fontUrl = fontUrl.group().split(',')[-1][:-1]
comparisonTable = parse_font(fontUrl)
result=html.xpath("//div[@id='ranks-list']/ul[@class='row']")
for row in result[:10]:
    row_list = []
    rank = int(row.xpath("li[1]/text()")[0])
    name = row.xpath("li[2]/p[1]/text()")[0]
    boxOffice = convert(row.xpath('li[3]/i/text()')[0], comparisonTable)
    print(rank, name, date, boxOffice)