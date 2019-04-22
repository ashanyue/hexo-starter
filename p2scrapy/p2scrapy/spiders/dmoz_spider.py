# coding=UTF-8
import scrapy
from scrapy.http import Request, FormRequest
from p2scrapy.items import P3ScrapyItem
from bs4 import BeautifulSoup
import re
import os

class DmozSpider(scrapy.Spider):
    name = "dmoz"
    allowed_domains = ["flw.ph"]
    start_urls = [
        "http://www.flw.ph/forum-86-1.html",
        "http://www.flw.ph/forum-47-1.html"

    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36',
        "Referer": "http://www.flw.ph/",
        "cookie": "__cfduid=d3727f653bfb01d1ae6df641f006647a31552719307; z67S_2132_saltkey=JBkSj2h9; z67S_2132_lastvisit=1552715707; pgv_pvid=9252667769; ts_uid=4017039504; _ga=GA1.2.1299151893.1552719318; _uab_collina=155271932699977223172644; z67S_2132_ulastactivity=3900sGLHLR2pMn316TXLkvdV%2BsGNwx5zulqFtbdRZ5wuBFaAX88f; z67S_2132_lastcheckfeed=63111%7C1552719333; z67S_2132_connect_is_bind=0; z67S_2132_smile=1D1; z67S_2132_atarget=1; z67S_2132_pc_size_c=0; CURAD=1; z67S_2132_sid=txa90o; z67S_2132_visitedfid=86D76D70D40D47D67; z67S_2132_sendmail=1; pgv_info=ssid=s243732460; ts_last=www.flw.ph/forum-86-3.html; _gid=GA1.2.787758430.1552898902; z67S_2132_st_t=0%7C1552899006%7Cbc2c28eede5ee51c7f73b5720208bb96; z67S_2132_forum_lastvisit=D_86_1552899006; z67S_2132_lastact=1552899012%09forum.php%09image"
    }

    # login_url = "http://www.flw.ph/member.php?mod=logging&action=login&referer=http://www.flw.ph/&infloat=yes&handlekey=login&inajax=1&ajaxtarget=fwin_content_login"

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, meta={'proxy': 'http://0.0.0.0:1087'}, callback=self.parse)

    #
    # def post_login(self, response):
    #     # _selector = Selector(text=response.body)
    #    # _temp = etree.parse(StringIO(response.body))
    #     print(Selector(response).xpath("//root").extract()[0])

    def parse(self, response):

        list = response.css("th.new.forumtit")
        for detail in list:
            detail_url = detail.css("a")[0].css('::attr(href)').extract_first("")
            detail_url = "http://www.flw.ph/" + detail_url
            date_time = detail.css(".foruminfo p.z::text").extract_first("")
            date_time = date_time.replace('\n', '').replace('\n', '').replace(u'发表于', '').strip()

            typeid = re.findall(r'forum-(\d+)', response.url)[0]
            articleID = re.findall(r'thread-(\d+)', detail_url)[0]
            dir = 'other'
            if typeid == '47':
                dir = 'sharing'
            elif typeid == '86':
                dir = 'used'
            else:
                dir = 'other'

            prefixPath = '/Users/robbin/Documents/Work/hexo-starter/source/_posts/'
            mdFilePath = prefixPath + dir + '/' + articleID + '.md'

            if os.path.exists(mdFilePath) == False:
                yield Request(url=detail_url,
                              meta={"date_time": date_time, 'type': re.findall(r'forum-(\d+)', response.url)[0],
                                    'mdFilePath': mdFilePath, 'categories': dir}, callback=self.parse_detail)
            else:
                print('exists[' + mdFilePath + '] skip..')


        nextUrl = response.css("a.nxt").css('::attr(href)').extract_first("")
        page = int(re.findall(r'forum-\d+-(\d+)', nextUrl)[0])
        print(int(page))
        if len(nextUrl)>0 and page <=3:
            yield Request(url="http://www.flw.ph/" + nextUrl, callback=self.parse)

    def parse_detail(self, response):
        # print("=======")
        title = response.css("#thread_subject::text").extract_first("")
        # _content = response.css("td.t_f")
        content = response.css("td.t_f").extract_first()
        soup = BeautifulSoup(content, features="lxml")
        loginTag = soup.find('div', {"class": "attach_nopermission"})
        if hasattr(loginTag, "extract"):
            loginTag.extract()

        iTag = soup.find('i', {'class': 'pstatus'})
        if hasattr(iTag, "extract"):
            iTag.extract()

        imgTips = soup.find_all('div', {'class': 'aimg_tip'})
        for imgTip in imgTips:
            if hasattr(imgTip, "extract"):
                imgTip.extract()

        tdTag = soup.find('td')
        imgtags = tdTag.find_all('img')
        for img in imgtags:
            img["onclick"] = ''
            img["onmouseover"] = ''
            img["onmouseover"] = ''
            imgFile = ''
            try:
                imgFile = img['file']
            except Exception as e:
                pass
            try:
                imgFile = img['zoomfile']
            except Exception as e:
                pass

            trueSrc = imgFile
            if len(imgFile) > 0:
                if imgFile.count('http:') <= 0 and imgFile.count('https:') <= 0:
                    trueSrc = 'http://www.flw.ph/' + trueSrc
                img['src'] = trueSrc
                # print(img['src'])

        content1 = str(tdTag)
        content1 = content1.replace('<ignore_js_op>', '').replace('</ignore_js_op>', '')
        description = soup.get_text().replace('\n', '')
        date_time = response.meta['date_time']
        # print(title,response.meta['date_time'],len(content),response.url)
        # print("=======")

        item = P3ScrapyItem()
        item['id'] = re.findall(r'thread-(\d+)', response.url)[0]
        item['type'] = response.meta['type']
        item['title'] = title
        item['content'] = content1
        item['date_time'] = date_time
        item['url'] = response.url
        item['keywords'] = title
        item['description'] = description.replace('\n', '').replace('\r', '').replace(' ','').replace(' ','')
        if len(item['description'])>120:
            item['description'] = item['description'][0:120]
        item['mdFilePath'] = response.meta['mdFilePath']
        item['categories'] = response.meta['categories']
        if len(item['description']) >= 40 or len(imgtags) > 0:
            yield item