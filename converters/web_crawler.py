import requests
from bs4 import BeautifulSoup
import urllib.parse
import markdownify

def get_page_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def extract_links(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    links = set()
    
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        # 处理相对链接
        absolute_url = urllib.parse.urljoin(base_url, href)
        links.add(absolute_url)
    
    return links

def html_to_markdown(html):
    """将HTML内容转换为Markdown格式"""
    return markdownify.markdownify(html)

def crawl_website(start_url, max_depth=1, output_format='html'):
    """
    爬取网站
    :param start_url: 起始URL
    :param max_depth: 最大爬取深度
    :param output_format: 输出格式，'html'或'markdown'
    """
    visited = set()
    to_visit = [(start_url, 0)]
    
    while to_visit:
        url, depth = to_visit.pop(0)
        
        if url in visited or depth > max_depth:
            continue
            
        print(f"Crawling: {url} (depth {depth})")
        html = get_page_content(url)
        if not html:
            continue
            
        if output_format == 'markdown':
            content = html_to_markdown(html)
        else:
            content = html
            
        visited.add(url)
        links = extract_links(html, url)
        
        for link in links:
            if link not in visited:
                to_visit.append((link, depth + 1))
    
    return visited

if __name__ == "__main__":
    target_url = input("请输入要抓取的网站URL: ")
    output_format = input("请输入输出格式(html/markdown，默认为html): ") or 'html'
    crawled_pages = crawl_website(target_url, output_format=output_format)
    print(f"\n抓取完成，共找到 {len(crawled_pages)} 个页面:")
    for page in crawled_pages:
        print(page)