import html
from lxml import etree
from urllib.parse import urljoin

class ChapterParser():
    '''
    description: 解析子章节，也就是class为chapter的html内容
    param {*} self
    param {*} original 原始的text
    param {*} index_title 标题
    param {*} baselevel 章节对应的级别，例如1.1 或1.1.1这种
    return {*}
    '''    
    def __init__(self, base_url,original,index_title, baselevel=0):
        self.heads = {'h1': 1, 'h2': 2, 'h3': 3, 'h4': 4, 'h5': 5, 'h6': 6}
        self.original = original
        self.baselevel = baselevel
        self.index_title = index_title
        self.base_url = base_url

    @classmethod
    def titleparse(cls, li):
        '''
        description: 从li标签中提取出text作为title
        return {title}
        '''        
        children = li.getchildren()
        if len(children) != 0:
            firstchildren = children[0]
            primeval_title = ''.join(firstchildren.itertext())
            title = ' '.join(primeval_title.split())
        else:
            title = li.text
        return title
    
    def parser(self):
        tree = etree.HTML(self.original)
        if tree.xpath('//section[@class="normal markdown-section"]'):
            context = tree.xpath('//section[@class="normal markdown-section"]')[0]
        else:
            context = tree.xpath('//section[@class="normal"]')[0]
        if context.find('footer'):
            context.remove(context.find('footer'))
        # 解析
        context = self.parse_img(context)
        # 解析head
        context = self.parsehead(context)
        # 返回html格式的内容
        return html.unescape(etree.tostring(context,encoding='utf-8').decode())

    def parse_img(self,context):
        el_imgs = context.xpath('//img')
        for el_img in el_imgs:
            old_src = el_img.get('src')
            new_src = urljoin(self.base_url,old_src)
            el_img.set('src',new_src)
        return context

    def parsehead(self, context):
        def level(num):
            return 'level' + str(num)
        for head in self.heads:
            if context.xpath(head):
                self.head = self.titleparse(context.xpath(head)[0])
                if self.head in self.index_title:
                    context.xpath(head)[0].text = self.index_title
                context.xpath(head)[0].attrib['class'] = level(self.baselevel)
                break
        return context