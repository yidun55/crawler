#coding:utf-8

from scrapy.http import Request, FormRequest
from scrapy.selector import HtmlXPathSelector
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

def frequest_51auto(response):
    hxs = HtmlXPathSelector(response)
    car_id, = hxs.select("//a[@class='oa_ratio _compare_trigger']/@carid").extract()
    url = "http://www.51auto.com/dwr/exec/CarViewAJAX.getCarInfoNew"
    params = {
        "callCount": "1", 
        "c0-scriptName": "CarViewAJAX", 
        "c0-methodName": "getCarInfoNew", 
        #"c0-id": "1202_1382667852398", 
        "c0-param0": "number:%s" % car_id, 
        "xml": "true"
    }
    
    headers = {"Referer": response.url}
    request = FormRequest(url=url, formdata=params,
                          headers=headers)
    return request

def frequest_che168(response):
    hxs = HtmlXPathSelector(response)
    url = hxs.select("//script/text()")\
          .re("AutoJsLoad({url:'(http://www\.interface\.che168\.com/quoted/dealerminpricebyspec\.ashx\?.*&_callback=show4sNewPrice)'});")

    if url:
        headers = {"Referer": response.url}
        request = Request(url=url[0], headers=headers)
        return request

def frequest_58(response):
    hxs = HtmlXPathSelector(response)
    url = "http://user.58.com/userdata/?callback=jsonp6283&userid=%s&type=58&dispcateid=29"

    userid, = hxs.select("//script").re("userid:'(.*)',linkman")
    headers = {"Referer": response.url}
    request = Request(url=url % userid, headers=headers)
    return request

def frequest_zg2sc(response):
    hxs = HtmlXPathSelector(response)
    shop_url = hxs.select(u"//div[@class='carfile_jxs']//a[contains(text(), '进入店铺')]/@href").extract()
    if shop_url:
        headers = {"Referer": response.url}
        return Request(url=urljoin_rfc(get_base_url(response), shop_url[0]), headers=headers)

def frequest_cn2che(response):
    """
    <?xml version="1.0" encoding="utf-8" ?><rep><opt>succ</opt><carview>3</carview><qq>2636953885</qq><qq1></qq1><qq2></qq2><address>宁波市江东南路313号日月星城小区西大门（原光大银行）</address><linkname>小赵</linkname><mobile>400-8880267</mobile><member_fax></member_fax><member_provice>浙江</member_provice><member_city>宁波</member_city><member_xian>江东区</member_xian><member_phone_1>130</member_phone_1><member_phone_2>56717816</member_phone_2><member_shop_name>宁波安信卡卡汽车经纪有限公司</member_shop_name><member_email>1779858435@qq.com</member_email><member_access>nb2car</member_access><access>nb2car</access><suserid>000126376</suserid><shop_starttime>2013/6/25 0:00:00</shop_starttime><shop_starttime>2013/6/25 0:00:00</shop_starttime><shop_endtime>2014/6/30 0:00:00</shop_endtime><shop_level>2</shop_level><shop_isopen>1</shop_isopen><serive1></serive1><serive2></serive2><serive3></serive3><serive4></serive4><serive5></serive5><serive6></serive6><serive7></serive7><serive8></serive8><serive9></serive9><serive10></serive10><serive11></serive11><serive12></serive12><BusinessAuthentication>2</BusinessAuthentication><EmailAuthentication>1</EmailAuthentication><IdentityAuthentication>0</IdentityAuthentication><MobileAuthentication>1</MobileAuthentication><member_sell_total>34940</member_sell_total><member_sellcount>97</member_sellcount><selled>22455</selled><shop_view>29790</shop_view><point>121.558133,29.861049</point></rep>
    """
    hxs = HtmlXPathSelector(response)
    url = "http://www.cn2che.com/buycar/sellcarinfo_html.aspx"
    
    hidchildid = ''.join(hxs.select("//input[@id='hidchildid']/@value").extract())
    hiduserid = ''.join(hxs.select("//input[@id='hiduserid']/@value").extract())
    car_id = ''.join(hxs.select("//span[@id='carid']/text()").extract())
    hidcar_city_id = ''.join(hxs.select("//input[@id='hidcar_city_id']/@value").extract())
    params = {
        "action": "carviewmember", "userchild": hidchildid,
        "userid": hiduserid, "carid": car_id, "car_city_id": hidcar_city_id
    }

    headers = {"Referer": response.url}
    return FormRequest(url=url, formdata=params, headers=headers)

