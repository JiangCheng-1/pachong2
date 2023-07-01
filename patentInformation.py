import re
import requests
from urllib.parse import quote
from requests.exceptions import RequestException


headers = {
    'User-Agent': 'Mozilla/5.0(Macintosh;Intel Mac OS X 10_13_3)AppleWebkit/537.36(KHTML,like Gecko)Chrome/65.0.3325.162 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'Cookie': 'HWWAFSESID=6fa79ba494c27589ca0; HWWAFSESTIME=1688089042887; csrfToken=lit8TfC5GznaqR9EArHD2pql; TYCID=aacd3b5016e611eea674a7d35e4a883c; sajssdk_2015_cross_new_user=1; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2218909f2b21a9a4-09e3464dad8bd58-3d267449-921600-18909f2b21b3fb%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTg5MDlmMmIyMWE5YTQtMDllMzQ2NGRhZDhiZDU4LTNkMjY3NDQ5LTkyMTYwMC0xODkwOWYyYjIxYjNmYiJ9%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%22%2C%22value%22%3A%22%22%7D%2C%22%24device_id%22%3A%2218909f2b21a9a4-09e3464dad8bd58-3d267449-921600-18909f2b21b3fb%22%7D; Hm_lvt_e92c8d65d92d534b0fc290df538b4758=1688089048; bannerFlag=true; searchSessionId=1688089133.71964003; Hm_lpvt_e92c8d65d92d534b0fc290df538b4758=1688089183'
}


# 使用request.get()获取网页
def get_one_page(url):
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            response.encoding = 'utf-8'
            return response.text
        return '页面无反应'
    except RequestException:
        return 'Request出现错误'


# 根据关键词搜索公司
def get_company(keyWord):
    href = 'https://www.tianyancha.com/search?key={}'.format(quote(keyWord))
    html = get_one_page(href)
    # 使用compile函数将正则表达式的字符串形式编译成一个pattern对象
    pattern = re.compile(
        '<a class="index_alink__zcia5 link-click".*?href="(.*?)".*?<span>(.*?)</span>',
        re.S)
    # 找到最符合关键词的公司（搜索出的第一个结果）
    item = re.findall(pattern, html)[0]
    # 对公司名称进行清洗
    name = re.sub('(<em>|</em>)', '', item[1])
    yield {
        '公司名称': name,
        '公司网址': item[0].strip()
    }


# 获取专利信息
def get_patents(url):
    html = get_one_page(url)
    # 使用compile函数将正则表达式的字符串形式编译成一个pattern对象
    pattern = re.compile(
        'title":"(.*?)".*?"patentNum":"(.*?)".*?"uuid":"(.*?)".*?"pubnumber":"(.*?)".*?"applicationTime":"(.*?)".*?'
        '"inventor":"(.*?)".*?"pubDate":"(.*?)".*?"patentType":"(.*?)".*?"lprs":"(.*?)"',
        re.S)
    items = re.findall(pattern, html)
    for item in items:
        # 获取详情页链接
        href = 'https://zhuanli.tianyancha.com/' + item[2]
        yield {
            '申请日': item[4].strip(),
            '专利名称': item[0].strip(),
            '专利类型': item[7].strip(),
            '专利状态': item[8].strip(),
            '申请号': item[1].strip(),
            '公开（公布）号': item[3].strip(),
            '公开（公告）日': item[6].strip(),
            '发明人': item[5].strip(),
            '详情链接': href
        }


if __name__ == '__main__':
    # 搜索公司，获取公司网址
    key_word = '华为技术'
    company = list(get_company(key_word))
    company_name = company[0]['公司名称']
    company_url = company[0]['公司网址']
    content = get_one_page(company_url)
    print(content)

    # 获取公司的专利信息列表
    # 专利信息链接 = 'https://capi.tianyancha.com/cloud-intellectual-property/patent/patentListV6?_='
    #                 + '1688189277816'      这个不知道是什么数字，在网页中搜索没搜到，所以没能获得某个公司的全部专利信息
    #                 + '&id=24416401'       公司id（包含在company_url最后面的一串数字）
    #                 + '&pageSize=10'       每页有10条专利信息
    #                 + '&pageNum=1'         分页数
    #                 + '&type=-100&lprs=-100&applyYear=-100&pubYear=-100&fullSearchText=&sortField=&sortType=-100'
    patent_list = list(get_patents('https://capi.tianyancha.com/cloud-intellectual-property/patent/patentListV6?_=1688189277816&id=24416401&pageSize=10&pageNum=1&type=-100&lprs=-100&applyYear=-100&pubYear=-100&fullSearchText=&sortField=&sortType=-100'))
    print(patent_list)
    print(len(patent_list))
