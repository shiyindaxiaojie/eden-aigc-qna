import requests
from bs4 import BeautifulSoup
import urllib3

# 禁用SSL验证
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 定义要抓取的URL
url = 'http://youzhiyouxing.cn/materials'

# 发送请求并获取HTML内容
response = requests.get(url, verify=False)
html_content = response.text

# 使用Beautiful Soup解析HTML内容
soup = BeautifulSoup(html_content, 'html.parser')

# 找到“推荐文章”部分
recommendation_section = soup.find('div', {'class': 'recommendation'})

# 找到“推荐文章”部分中的所有按钮
buttons = recommendation_section.find_all('tw-items-center')

# 点击每个按钮并抓取出现的内容
for button in buttons:
    # 通过向“data-url”属性中指定的URL发送POST请求来单击按钮
    post_data = {'_csrf': soup.find('input', {'name': '_csrf'})['value']}
    response = requests.post(button['data-url'], data=post_data, verify=False)

    # 解析单击按钮后出现的页面的HTML内容
    content_soup = BeautifulSoup(response.text, 'html.parser')

    # 从页面中抓取您想要的内容
    # 例如，您可以像这样找到文章标题：
    article_titles = content_soup.find_all('h3', {'class': 'title'})

    # 输出每篇文章的标题和URL
    for title in article_titles:
        print(title.text)
        print(title.find('a')['href'])