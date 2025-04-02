import requests
from lxml import etree
import re
import xlwt
from tqdm import tqdm
import warnings

# 忽略所有警告
warnings.filterwarnings('ignore')

# 设置请求头和cookies，模拟浏览器请求
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Cookie': 'session-id=143-2799974-3213333; ubid-main=132-3744519-7365960; sp-cdn="L5Z9:NZ"; skin=noskin; x-main=5PBhOmFz9RtPFFXUBbnKYuaHCwZklC69LD7k7ff5fkqzecau9Nrb25yFVLSmmwdU; at-main=Atza|IwEBIIJnF62YSbglzb6NeFyLwxsKJo5O6xrZmVZBkEyZhvJXMCgfcGLMkjbWmWbl4689RxX54BZPk0kfyUVd7CFUnC3EcaoBl8ypLfZvyQLyfYBkG4giCBIcxeQUms4VTAXkpc4VKHhqwjIZOcvwT2bapvTAntkw1k1NDXTKqSCH5bdzIPTOvu3M7n5BOf8iy-oVUFTHp-xmYkNmfT9DyQo3MdY3Bs_SlVSH_PukYog8tX0Z2w; sess-at-main="dqdsHIIFgM7UT2e7S5XuFlVFquwKkP+7n6R6Q4VvJFI="; sst-main=Sst1|PQEllRPM9qhWMSanv0eGgTLZCTZKMeuockTyrkQ3iGmZ51ZSswGjAQXhPk-eak9AJWkRunbTD4ffhWw0MtaOiXHIVrXa9xqjMLZmsx9cJoC77dOaKSk9uePaOpuKdXkzoJQsLb1vskxQAYMqhY7OF0-LECOoXKgNU1xzX3rw6wQQZqRvYSoXl9u0ZmlOYRE8MJjN8n2jT-KGqwPcvXseq_t8O29OT6FBNxEYxmCktGg06o6F27dr_msZrE4AHfSB6Ep4qHeyq19DUJuGTqv0VGJ71pxP-gXB-XZqTtEZPLxaAp0; lc-main=zh_CN; session-id-time=2082787201l; i18n-prefs=USD; session-token=L81/BGpH0r48hgzYx019TyWtiG4V91hLJHcr5aJwvdGMtaQYRsnyqet642vvG4tK6XsQYHFTEzPz5HhdauwDEcxJsBi9Fnl1J8mwZEjGWrxv4zO1PKgqYYMqB06btAd7C6If+eBMKnEJ0rZbJ+3zuV4eM1YAAr0R+tRJi6ERIptsG6+BzE8DVAfgt8gwHml9X7MGlo/BMlgEfBH2JvQnpPz1eQ62xm4cPM9yiLGUd9xUoh6n4vqEfxkdYNcG598s+3OrXIe9zSkQeDbKkU3JwYIXNFsuRs+BSwGq3UOWcN6gD8OUtE9X2zVnyJot3SWs1DHkgMzbjyIHnbCVLDWhLPOWrCoN+ys4BY4Fdvi5HRCJcG1f5qLZMX494SyMLalD'
}


# 解析网页并提取所需数据
def parse_page(url):
    try:
        response = requests.get(url=url, headers=headers, verify=False)  # 添加 verify=False
        response.raise_for_status()  # 如果发生HTTP错误，抛出异常
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page: {e}")
        return []

    html = etree.HTML(response.text) # 使用etree.HTML解析传入的HTML内容，将其转换为可以进行XPath查询的对象。
    comments = html.xpath('//div[@id="cm_cr-review_list"]/div')
    reviews = []

    for comment in comments:
        ratings = comment.xpath('.//span[@class="a-icon-alt"]/text()') # 提取用户评分
        comments_text = comment.xpath(
            './/span[@class="cr-original-review-content"]/text() | .//span[@class="cr-original-review-content"]/br') # 提取评论文本


        # 处理评论文本，合并所有部分，包括换行符
        full_comment = ""
        for part in comments_text:
            if isinstance(part, etree._Element) and part.tag == 'br':
                full_comment += '\n'
            else:
                full_comment += part.strip() + ' ' # 检查是否是换行符。如果是，添加换行符；否则，去除前后空格后添加到 full_comment 中。

        for rating in ratings:
            rating_value = re.sub('颗星，最多 5 颗星', '', rating)
            sentiment = '1' if float(rating_value) >= 3.5 else '0' # 评分大于等于3.5的为正面（'1'），否则为负面（'0'）。
            reviews.append((full_comment if full_comment else 'No title', rating_value, sentiment))
    return reviews


# 主函数，处理多页评论数据，并存入Excel
def main():
    # 好评
    pos_urls = [
        'https://www.amazon.com/-/zh/product-reviews/B09Y8K2HJN/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=five_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B09HM94VDS/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=five_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B07WCW1PB3/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=five_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B00BIFNTMC/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=five_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B01JPOLKDW/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=five_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B004YAVF8I/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=five_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B005EJH6Z4/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=five_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B015NBTAOW/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=five_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B087Z5WDJ2/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=five_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B0787D6SGQ/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=five_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B07H8TJMX7/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=five_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B098S48QWM/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=five_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B0836GXKKB/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=five_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B087Z733CM/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=five_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B09Y8K2HJN/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=four_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B09HM94VDS/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=four_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B07WCW1PB3/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=four_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B00BIFNTMC/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=four_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B01JPOLKDW/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=four_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B004YAVF8I/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=four_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B005EJH6Z4/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=four_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B015NBTAOW/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=four_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B087Z5WDJ2/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=four_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B0787D6SGQ/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=four_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B07H8TJMX7/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=four_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B098S48QWM/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=four_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B0836GXKKB/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=four_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B087Z733CM/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=four_star&pageNumber=',
    ]
    # 差评
    neg_urls = [
        'https://www.amazon.com/-/zh/product-reviews/B09Y8K2HJN/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=one_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B09HM94VDS/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=one_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B07WCW1PB3/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=one_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B00BIFNTMC/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=one_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B01JPOLKDW/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=one_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B004YAVF8I/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=one_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B005EJH6Z4/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=one_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B015NBTAOW/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=one_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B087Z5WDJ2/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=one_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B0787D6SGQ/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=one_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B07H8TJMX7/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=one_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B098S48QWM/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=one_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B0836GXKKB/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=one_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B087Z733CM/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=one_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B09Y8K2HJN/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=two_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B09HM94VDS/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=two_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B07WCW1PB3/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=two_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B00BIFNTMC/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=two_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B01JPOLKDW/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=two_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B004YAVF8I/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=two_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B005EJH6Z4/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=two_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B015NBTAOW/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=two_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B087Z5WDJ2/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=two_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B0787D6SGQ/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=two_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B07H8TJMX7/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=two_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B098S48QWM/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=two_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B0836GXKKB/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=two_star&pageNumber=',
        'https://www.amazon.com/-/zh/product-reviews/B087Z733CM/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=two_star&pageNumber=',
    ]

    workbook0 = xlwt.Workbook(encoding='utf-8')
    sheet0 = workbook0.add_sheet('Reviews')
    sheet0.write(0, 0, "评论内容")
    sheet0.write(0, 1, "评分")
    sheet0.write(0, 2, "评价")

    workbook1 = xlwt.Workbook(encoding='utf-8')
    sheet1 = workbook1.add_sheet('Reviews')
    sheet1.write(0, 0, "评论内容")
    sheet1.write(0, 1, "评分")
    sheet1.write(0, 2, "评价")
    # 好评和差评的网址数量
    pos_urls_count = len(pos_urls)
    neg_urls_count = len(neg_urls)
    total_urls_count = pos_urls_count + neg_urls_count

    # 总进度条
    with tqdm(total=total_urls_count * 10, desc='Processing reviews') as pbar:
        row = 1
        for base_url in pos_urls:
            for page_num in range(1, 11):  # 10页
                url = f'{base_url}{page_num}'
                reviews = parse_page(url)
                for content, rating, sentiment in reviews:
                    sheet0.write(row, 0, content)
                    sheet0.write(row, 1, rating)
                    sheet0.write(row, 2, sentiment)
                    row += 1
                pbar.update(1)  # 更新进度条
        workbook0.save('pos_comment.xls')

        row = 1
        for base_url in neg_urls:
            for page_num in range(1, 11):  # 10页
                url = f'{base_url}{page_num}'
                reviews = parse_page(url)
                for content, rating, sentiment in reviews:
                    sheet1.write(row, 0, content)
                    sheet1.write(row, 1, rating)
                    sheet1.write(row, 2, sentiment)
                    row += 1
                pbar.update(1)  # 更新进度条
        workbook1.save('neg_comment.xls')

    print("Data saved to Excel successfully.")


if __name__ == '__main__':
    main()
