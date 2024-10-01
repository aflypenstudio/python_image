import os
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# 定義 headers 和 cookies
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
}
cookies = {'over18': '1'}

# 要抓取的頁面 URLs
urls = [
    'https://www.ptt.cc/bbs/Beauty/index.html',
]

# 主要儲存圖片和記錄檔的資料夾
save_folder = '/srv/dev-disk-by-uuid-522284dc-17fd-4ee4-a792-ff00dc3ae711/Downloads/PTT_Images'
if not os.path.exists(save_folder):
    os.makedirs(save_folder)

# 建立已處理連結的 cache 檔案 cached.txt
cache_file = os.path.join(save_folder, 'cached.txt')
if not os.path.exists(cache_file):
    with open(cache_file, 'w') as f:
        pass

# 載入已經處理過的連結
with open(cache_file, 'r') as f:
    cached_links = f.read().splitlines()

# 抓取每個頁面的函數
def scrape_page(url):
    res = requests.get(url, headers=headers, cookies=cookies)
    soup = BeautifulSoup(res.text, 'html.parser')

    # 取得每篇文章
    for r_ent in soup.find_all('div', class_='r-ent'):
        title_tag = r_ent.find('div', class_='title').find('a')
        if title_tag and '[公告]' not in title_tag.text:
            post_url = 'https://www.ptt.cc' + title_tag['href']
            title = title_tag.text.strip().replace('?', '')  # 避免非法字元

            # 如果該文章的連結已經處理過，則略過
            if post_url in cached_links:
                print(f"已處理過 {post_url}，略過。")
                continue

            print(f"處理 {post_url}")
            process_post(post_url, title)

# 處理每篇文章並下載圖片的函數
def process_post(post_url, title):
    res = requests.get(post_url, headers=headers, cookies=cookies)
    soup = BeautifulSoup(res.text, 'html.parser')

    # 每篇文章對應的資料夾
    today = datetime.now().strftime('%Y%m%d')
    folder_name = f"{today}_{title}"
    post_folder = os.path.join(save_folder, folder_name)
    if not os.path.exists(post_folder):
        os.makedirs(post_folder)

    # 儲存圖片連結的檔案 captured_links.txt
    captured_links_file = os.path.join(post_folder, 'captured_links.txt')

    # 先將文章連結寫入 captured_links.txt 的第一行
    with open(captured_links_file, 'w') as f:
        f.write(f"文章連結: {post_url}\n")

    # 找到文章中的 <span class="article-meta-value"> 到 <span class="f2"> 範圍
    main_content = soup.find('div', id='main-content')
    if main_content:
        start_span = main_content.find('span', class_='article-meta-value')
        end_span = main_content.find('span', class_='f2')

        if start_span and end_span:
            # 獲取這兩個範圍之間的內容
            content_within_range = ''
            for tag in start_span.find_all_next():
                if tag == end_span:
                    break
                content_within_range += str(tag)

            # 創建一個新的 BeautifulSoup 對象來解析這個範圍內的內容
            soup_within_range = BeautifulSoup(content_within_range, 'html.parser')

            # 取得圖片連結
            for img_tag in soup_within_range.find_all('a'):
                img_link = img_tag.get('href')
                if img_link and any(img_link.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                    # 將圖片連結寫入 captured_links.txt
                    with open(captured_links_file, 'a') as f:
                        f.write(img_link + '\n')
                    
                    print(f"圖片連結已儲存: {img_link}")
                    
                    # 嘗試下載圖片
                    download_image(img_link, post_folder)
    
    # 將文章連結加入 cached.txt
    with open(cache_file, 'a') as f:
        f.write(post_url + '\n')

# 下載圖片的函數
def download_image(url, folder):
    try:
        response = requests.get(url, headers=headers, stream=True)
        if response.status_code == 200:
            img_name = url.split('/')[-1]
            img_path = os.path.join(folder, img_name)
            with open(img_path, 'wb') as f:
                for chunk in response:
                    f.write(chunk)
            print(f"圖片已儲存: {img_path}")
        else:
            print(f"下載圖片失敗，來自 {url}，狀態碼: {response.status_code}")
    except Exception as e:
        print(f"下載 {url} 發生錯誤: {e}")

# 抓取每個 URL
for url in urls:
    scrape_page(url)
    time.sleep(3)  # 每頁間隔 3 秒，避免過度請求
