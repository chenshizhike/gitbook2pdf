'''
Author: robert zhang <robertzhangwenjie@gmail.com>
Date: 2022-11-12 12:05:59
LastEditTime: 2022-11-13 09:55:57
LastEditors: robert zhang
Description: 
'''
import os
import socket
import requests
import asyncio
import weasyprint
from io import BytesIO
from bs4 import BeautifulSoup
from lxml import etree
from tqdm import tqdm
from urllib.parse import urljoin
from PyPDF2 import PdfReader, PdfMerger
from .ChapterParser import ChapterParser
from .HtmlGenerator import HtmlGenerator

BASE_DIR = os.path.dirname(__file__)
OUT_DIR = "./output"

def load_gitbook_css():
    with open(
        os.path.join(BASE_DIR, './libs/gitbook.css'), 'r'
    ) as f:
        return f.read()

def get_html(url):
    headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    }
    return requests.get(url,headers=headers, timeout=10).text  

class Gitbook2PDF():
    def __init__(self, base_url, fname=None):
        self.fname = fname
        if os.path.isdir(base_url):
            base_url = os.path.abspath(base_url)
        self.base_url = base_url
        self.content_list = []
        
        # If the output file name is not provided, grab the html title as the file name.
        if not self.fname:
            text = get_html(base_url)
            soup = BeautifulSoup(text, 'html.parser')
            title_ele = soup.find('title')
            if title_ele:
                title = title_ele.text
                if '·' in title:
                    title = title.split('·')[1]
                if '|' in title:
                    title = title.split('|')[1]
                title = title.replace(' ', '').replace('/', '-')
                self.fname = title + '.pdf'

    def run(self):
        content_urls = self.collect_urls()           
        self.content_list = ["" for _ in range(len(content_urls))]
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.crawl_main_content(content_urls))
        loop.close()
        
        merger = PdfMerger()
        bmparent = None
        print("生成PDF " + self.fname)
        phar = tqdm(total=len(content_urls))
        for index,obj in enumerate(content_urls):
            phar.set_description("处理中 ： %s" % obj['title'])
            html_g = HtmlGenerator(self.base_url)
            html_g.add_body(self.content_list[index])
            html_text = html_g.output()
            css_text = load_gitbook_css()
            
            if not os.path.exists(OUT_DIR+"_build") :
                os.makedirs(OUT_DIR+"_build")
            with open(OUT_DIR+"_build/" +str(index)+".html","w",encoding="utf-8") as f:
                f.write(html_text)
            
            byte = self.write_pdf(html_text,css_text)
            reader = PdfReader(BytesIO(byte));
            if obj['level'] == 2:
                bmparent = merger.add_outline_item(obj['title'],pagenum=len(merger.pages));
            else :
                merger.add_outline_item(obj['title'],parent=bmparent,pagenum=len(merger.pages));
            merger.append(reader,import_outline=False)
            phar.update()
            
        phar.set_description("处理完成！")   
        phar.close()
        with open(os.path.join(OUT_DIR,self.fname), "wb") as f:
            merger.write(f)
        print('生成PDF ',self.fname,'完成!')

    def write_pdf(self,html_text,css_text):
        tmphtml = weasyprint.HTML(string=html_text)
        tmpcss = weasyprint.CSS(string=css_text)
        try:
            return tmphtml.write_pdf(stylesheets=[tmpcss])
        except socket.timeout:
            print('socket.timeout: retry!')
            return tmphtml.write_pdf(stylesheets=[tmpcss])


    
    async def crawl_main_content(self, content_urls):
        tasks = []
        for index, urlobj in enumerate(content_urls):
            # 当urljob中的url不为空时，则表示为子章节，则开始爬取内容
            if urlobj['url']:
                tasks.append(self.gettext(index, urlobj['url'], urlobj['level'],urlobj['title']))
            else:
                tasks.append(self.getext_fake(index, urlobj['title'], urlobj['level']))
        await asyncio.gather(*tasks)
        # print("crawl : all done!")

    async def getext_fake(self, index, title, level):
        await asyncio.sleep(0.01)
        class_ = 'level' + str(level)
        string = f"<h1 class='{class_}'>{title}</h1>"
        self.content_list[index] = string

    async def gettext(self, index, url, level, title):
        '''
        description: 爬取url中的内容
        return path's html
        '''
        metatext = get_html(url)
        try:
            text = ChapterParser(url,metatext, title, level ).parser()
            self.content_list[index] = text
        except IndexError:
            print('faild at : ', url, ' maybe content is empty?')

    def collect_urls(self):
        '''
        description: 获取页面中所有的章节url
        return {list[{
            url,
            level,
            title
        }]}
        '''
        found_urls = []
        content_urls = []
        text = get_html(self.base_url)
        lis = etree.HTML(text).xpath("//ul[@class='summary']//li")
        for li in lis:
            element_class = li.attrib.get('class')
            if not element_class:
                continue
            # 解析章节中的title和level
            if 'header' in element_class:
                title = self.titleparse(li)
                data_level = li.attrib.get('data-level')
                level = len(data_level.split('.')) if data_level else 1
                content_urls.append({
                    'url': "",
                    'level': level,
                    'title': title
                })
            elif "chapter" in element_class:
                data_level = li.attrib.get('data-level')
                level = len(data_level.split('.'))
                if 'data-path' in li.attrib:
                    data_path = li.attrib.get('data-path')
                    # url 为子章节的访问地址
                    url = urljoin(self.base_url, data_path)
                    # 解析子章节中的title
                    title = ChapterParser.titleparse(li)
                    # 将url、level、title 放入content_urls中
                    if url not in found_urls:
                        content_urls.append(
                            {
                                'url': url,
                                'level': level,
                                'title': title
                            }
                        )
                        found_urls.append(url)

                # Unclickable link
                else:
                    title = ChapterParser.titleparse(li)
                    content_urls.append({
                        'url': "",
                        'level': level,
                        'title': title
                    })
        return content_urls




