# -*- coding: utf-8 -*-
import scrapy
import json
from lxml import etree
import re
from truelove.items import TrueloveItem
from scrapy_redis.spiders import RedisSpider
import hashlib

class LoveSpider(RedisSpider):
    name = 'love'
    allowed_domains = ['zhenai.com']
    redis_key = 'love:start_urls'

    headers = {
        "Host": "search.zhenai.com",
        "Connection": "keep-alive",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
        "Referer": "http://search.zhenai.com/v2/search/pinterest.do?sex=1&agebegin=18&ageend=25&workcityprovince=-1&workcitycity=-1&h1=-1&h2=-1&salaryBegin=-1&salaryEnd=-1&occupation=-1&h=-1&c=-1&workcityprovince1=-1&workcitycity1=-1&constellation=-1&animals=-1&stock=-1&belief=-1&condition=66&orderby=hpf&hotIndex=&online=",
        # "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.8",
    }

    cookies = {
        "ipCityCode": "10102000",
        "LOGIN_FIRST108285148": "%5E%7EmemberId%3D108285148%5E%7EendDate%3D2017%E5%B9%B410%E6%9C%8823%E6%97%A5%5E%7Elogincount%3D1%5E%7E",
        "Hm_cv_2c8ad67df9e787ad29dbd54ee608f5d2": "1*gender*0",
        "Hm_lvt_2a6baf3863d1f0867a7fe97677668c12": "1508422983",
        "__utma": "185049014.313121358.1508422983.1508422983.1508422983.1",
        "__utmz=185049014.1508422983.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd": "(none)",
        "sid": "5uH0nPk5lesR7dXATBOn",
        "CHANNEL=^~refererHost=^~channelId=903404^~subid": "2^~",
        "ipOfflineCityCode": "10102000",
        "qqconnect": "%5E%7EopenId%3D7696E6981E7BC38DF4E79B2E6EE668E9%5E%7E",
        "login_health": "033525866e0e30646e301b38607e1926254951b6dbc6aa540f57bbf98a96614d98da58bd80380b89f6af4b76cde648dae82c85e32c1ab74879e20fc29e11981c",
        "preLG_108285148": "2017-10-19+22%3A22%3A57",
        "isSignOut": "%5E%7ElastLoginActionTime%3D1508464198721%5E%7E",
        "p": "%5E%7Eworkcity%3D10102008%5E%7Elh%3D108285148%5E%7Esex%3D0%5E%7Enickname%3D%E4%BC%9A%E5%91%98108285148%5E%7Emt%3D1%5E%7Eage%3D19%5E%7Edby%3D40d9884b99970379%5E%7E",
        "mid": "%5E%7Emid%3D108285148%5E%7E",
        "loginactiontime": "%5E%7Eloginactiontime%3D1508464198721%5E%7E",
        "logininfo": "%5E%7Elogininfo%3D18600672750%5E%7E",
        "rmpwd": "%5E%7Eloginmode%3D9%5E%7Elogininfo%3D18600672750%5E%7E",
        "otherinfo": "%5E%7Eisnew%3D1%5E%7E",
        "hds": "2",
        "live800": "%5E%7EisOfflineCity%3Dtrue%5E%7EinfoValue%3DuserId%253D108285148%2526name%253D108285148%2526memo%253D%5E%7E",
        "ooo": "%5E%7Esex%3D1%5E%7EworkCity%3D10102000%5E%7Eage2%3D19%5E%7Eage1%3D18%5E%7E",
        "bottomRemind": "%5E%7EisAuthGzt%3Dfalse%5E%7EvisPhoto%3Dno%5E%7E",
        "isvalideEmail": "%5E%7EvalideEmail%3D0%5E%7E",
        "dgpw": "1",
        "JSESSIONID": "abctDOz2Rz1s9aVhBE38v",
        "__xsptplusUT_14": "1",
        "Hm_lvt_2c8ad67df9e787ad29dbd54ee608f5d2": "1508412871,1508462278",
        "Hm_lpvt_2c8ad67df9e787ad29dbd54ee608f5d2": "1508464535",
        "__xsptplus14": "14.3.1508464108.1508464535.12%234%7C%7C%7C%7C%7C%23%232YBkFwitCztNVoI1kB_KdVTEx-BJahJQ%23",

    }

    # def start_requests(self):
    #     start_url = 'http://search.zhenai.com/v2/search/pinterest.do'
    #     # 发起请求获取页面搜索条件
    #     yield scrapy.Request(url=start_url,callback=self.parse,headers=self.headers,cookies=self.cookies)

    # 为了启动分布式爬虫而准备的
    def parse(self,response):
        start_url = 'http://search.zhenai.com/v2/search/pinterest.do'
        # 发起请求获取页面搜索条件
        yield scrapy.Request(url=start_url, callback=self.parse_start, headers=self.headers, cookies=self.cookies)

    # 解析搜索首页的处理
    def parse_start(self, response):
        html = response.body.decode('gbk')
        # print html

        sex_list = ['1']
        age_list = range(18,100)
        province = {}
        # {'10102001' : ['10102001', '10102002', '10102005', '10102006', '10102007', '10102008', '10102009', '10102010', '10102011', '10102012', '10102013', '10102014', '10102015', '10102016', '10102017', '10102018']}
        with open('city.html', 'r') as f:
            html = etree.HTML(f.read())
            city_div = html.xpath('//div[@class="city_box"]')
            for city in city_div:
                city_id_list = city.xpath('.//a/@v')
                province_id = city_id_list[0][:-2] + '00'
                province[str(province_id)] = city_id_list

        for key,value in province.items():
            print key,value

        base_url = 'http://search.zhenai.com/v2/search/getPinterestData.do?sex=%s&agebegin=%s&ageend=%s&workcityprovince=%s&workcitycity=%s&h1=-1&h2=-1&salaryBegin=-1&salaryEnd=-1&occupation=-1&h=-1&c=-1&workcityprovince1=-1&workcitycity1=-1&constellation=-1&animals=-1&stock=-1&belief=-1&condition=66&orderby=hpf&hotIndex=&online=&currentpage=%s&topSearch=false'

        for sex in sex_list:
            for age in age_list:
                for proid, city_list in province.items():
                    for cityid in city_list:
                        for page in range(1,101):
                            print sex,age,proid,cityid,page
                            fullurl = base_url % (str(sex),str(age),str(age),str(proid),str(cityid),str(page))
                            yield scrapy.Request(fullurl,callback=self.parse_list,headers=self.headers,cookies=self.cookies)

    # 解析列表页处理
    def parse_list(self,response):
        data = json.loads(response.body.decode('gbk'))
        data = data['data']
        base_url = 'http://album.zhenai.com/u/%s'
        # 生成详情请求
        for item in data:
            memberid = item['memberId']
            fullurl = base_url % memberid
            #priority 设置请求在队里的优先级
            yield scrapy.Request(url=fullurl,callback=self.parse_detail, headers=self.headers,cookies=self.cookies, priority=1)

    # 处理详情页
    def parse_detail(self,response):
        # print response.body.decode('gbk')
        # 提取详情页数据，组建item
        item = TrueloveItem()
        nick = response.xpath('//a[@class="name fs24"]/text()').extract()[0]
        age = response.xpath('//table[@class="brief-table"]//tr[1]/td[1]/text()').extract()[0]
        age = re.search(r'\d+',age).group()

        item['nick'] = nick
        item['age'] = age
        item['url'] = self.md5(response.url)
        # yield item
        print '生成item'
        yield item

    def md5(self,data):
        m = hashlib.md5()
        m.update(data)
        return m.hexdigest()

        # 单独获取省ID
        # with open('data.html','r') as f :
        #     html = f.read()
        #     html = etree.HTML(html)
        #     province = html.xpath('//ul[@class="area_box_tr"]/li/a/@v')


        # start_url = 'http://search.zhenai.com/v2/search/getPinterestData.do?sex=1&agebegin=18&ageend=18&workcityprovince=-1&workcitycity=-1&h1=-1&h2=-1&salaryBegin=-1&salaryEnd=-1&occupation=-1&h=-1&c=-1&workcityprovince1=-1&workcitycity1=-1&constellation=-1&animals=-1&stock=-1&belief=-1&condition=66&orderby=hpf&hotIndex=&online=&currentpage=100&topSearch=false'
        # yield scrapy.Request(url=start_url, callback=self.parse, headers=self.headers, cookies=self.cookies)
        #
        # data = response.body.decode('gbk')
        # data = json.loads(data) # 转成字典
        # # 格式化输出
        # print json.dumps(data,ensure_ascii=False, indent=4)
        #
        # data = data['data']
        # for item in data:
        #     print item