# -*- coding:utf-8 -*-
# /usr/bin/env python
"""
Author: Albert King
date: 2020/5/22 19:27
contact: jindaxiang@163.com
desc: 国家市场监督管理总局：首页 > 专题 > 市场监管战“疫”> 曝光台
自动采集内容和摘要生成
http://www.samr.gov.cn/zt/jjyq/bgt/
"""
import pandas as pd
import pyhanlp as nlp
import requests
from bs4 import BeautifulSoup
from gne import GeneralNewsExtractor
from urllib import parse

extractor = GeneralNewsExtractor()
headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cache-Control": "no-cache",
        "Host": "www.samr.gov.cn",
        "Pragma": "no-cache",
        "Proxy-Connection": "keep-alive",
        "Referer": "http://www.samr.gov.cn/zt/jjyq/bgt/index_1.html",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36",
    }


def get_url():
    """
    get all url from specific website
    :return:
    :rtype:
    """
    out_list = []
    url = "http://www.samr.gov.cn/zt/jjyq/bgt/index.html"
    r = requests.get(url, headers=headers)
    r.encoding = "utf-8"
    soup = BeautifulSoup(r.text, "lxml")
    js_text = soup.find(attrs={"language": "JavaScript"}).text
    page_num = js_text[js_text.find("//共多少页")-2:js_text.find("//共多少页")]
    need_list = soup.find(attrs={"class": "textRightTxt"}).find_all(attrs={"target": "_blank"})
    content_url_list = [item["href"].strip("../../../") for item in need_list]
    content_url_list = ["http://www.samr.gov.cn/zt/jjyq/bgt/" + item if item.startswith("2") else "http://www.samr.gov.cn/" + item for item in content_url_list]
    out_list.extend(content_url_list)
    for i in range(1, int(page_num)):
        print(f"正在采集第{i}页")
        url = f"http://www.samr.gov.cn/zt/jjyq/bgt/index_{i}.html"
        r = requests.get(url, headers=headers)
        r.encoding = "utf-8"
        soup = BeautifulSoup(r.text, "lxml")
        need_list = soup.find(attrs={"class": "textRightTxt"}).find_all(attrs={"target": "_blank"})
        content_url_list = [item["href"].strip("../../../") for item in need_list]
        pre_content_url_list = ["http://www.samr.gov.cn/zt/jjyq/bgt/" + item if item.startswith("2") else "http://www.samr.gov.cn/" + item for item in content_url_list]
        pre_content_url_list = [item.replace("http://www.samr.gov.cn/", "", 1) if "http://www.samr.gov.cn/http" in item else item for item in pre_content_url_list]
        pre_content_url_list = [item.replace("http://www.samr.gov.cn/zjdt/", "http://www.samr.gov.cn/zt/jjyq/zjdt/") if item.startswith("http://www.samr.gov.cn/zjdt/") else item for item in pre_content_url_list]
        out_list.extend(pre_content_url_list)
    return out_list


def extract_news_content(url: str) -> str:
    """
    get news content from the specific url
    :param url:
    :type url:
    :return:
    :rtype: str
    """
    r = requests.get(url, headers=headers)
    r.encoding = "utf-8"
    result = extractor.extract(r.text)
    return result["content"]


def extract_news(url: str) -> str:
    """
    get news content from the specific url
    :param url:
    :type url:
    :return:
    :rtype: str
    """
    r = requests.get(url, headers=headers)
    r.encoding = "utf-8"
    result = extractor.extract(r.text)
    return result


def generate_excel():
    all_url = get_url()
    print(len(all_url))
    big_list = []
    for page, url_item in enumerate(all_url):
        print(f"正在采集第{page}篇文章内容，请稍等")
        big_list.append(extract_news(url_item))
    temp_df = pd.DataFrame(big_list)

    des_list = []
    for item in temp_df["content"]:
        print(f"正在产生摘要：{nlp.HanLP.extractSummary(item, 2)[0]}")
        des_list.append(nlp.HanLP.extractSummary(item, 2)[0])

    temp_df["des"] = des_list
    data_df = temp_df[["title", "author", "publish_time", "des", "content"]]
    data_df.columns = ["信息名称", "信息来源", "发布时间", "具体描述", "内容"]
    need_df = data_df[["信息来源", "信息名称", "发布时间", "具体描述", "内容"]]
    need_df.to_excel("result.xlsx", encoding="utf_8_sig")


if __name__ == '__main__':
    generate_excel()
