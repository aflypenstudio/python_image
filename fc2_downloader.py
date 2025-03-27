import os
import requests
from bs4 import BeautifulSoup
import re
import urllib.request
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from threading import Thread
from tkinter.scrolledtext import ScrolledText

class FC2PPVDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("FC2-PPV 圖片下載器")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # 設置主題
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.create_widgets()
    
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 標題
        title_label = ttk.Label(main_frame, text="FC2-PPV 圖片下載器", font=('Arial', 14, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 15))
        
        # 文章編號輸入
        ttk.Label(main_frame, text="文章編號:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.article_entry = ttk.Entry(main_frame, width=30)
        self.article_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        self.article_entry.bind('<Return>', lambda event: self.start_download())  # 綁定Enter鍵
        
        # 保存路徑
        ttk.Label(main_frame, text="保存路徑:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.path_var = tk.StringVar()
        self.path_entry = ttk.Entry(main_frame, textvariable=self.path_var, width=40)
        self.path_entry.grid(row=2, column=1, sticky=tk.W, pady=5)
        self.path_var.set(os.getcwd())
        
        browse_btn = ttk.Button(main_frame, text="瀏覽...", command=self.browse_path)
        browse_btn.grid(row=2, column=2, padx=(5, 0))
        
        # 下載按鈕
        self.download_btn = ttk.Button(main_frame, text="開始下載", command=self.start_download)
        self.download_btn.grid(row=3, column=0, columnspan=3, pady=15)
        
        # 日誌區域
        ttk.Label(main_frame, text="日誌:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.log_area = ScrolledText(main_frame, height=15, width=70, state='disabled')
        self.log_area.grid(row=5, column=0, columnspan=3)
        
        # 進度條
        self.progress = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, length=500, mode='determinate')
        self.progress.grid(row=6, column=0, columnspan=3, pady=10)
        
        # 作者信息
        author_label = ttk.Label(main_frame, text="© 2023 FC2-PPV 圖片下載工具", foreground="gray")
        author_label.grid(row=7, column=0, columnspan=3, pady=(10, 0))
    
    def browse_path(self):
        path = filedialog.askdirectory()
        if path:
            self.path_var.set(path)
    
    def log_message(self, message):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')
        self.root.update()
    
    def update_progress(self, value):
        self.progress['value'] = value
        self.root.update()
    
    def start_download(self, event=None):  # 新增event參數以處理Enter鍵事件
        article_number = self.article_entry.get().strip()
        if not article_number:
            messagebox.showerror("錯誤", "請輸入文章編號！")
            return
        
        save_path = self.path_var.get()
        if not os.path.exists(save_path):
            messagebox.showerror("錯誤", "指定的保存路徑不存在！")
            return
        
        # 禁用按鈕防止重複點擊
        self.download_btn.config(state='disabled')
        self.log_message("開始下載任務...")
        self.update_progress(0)
        
        # 在新線程中執行下載
        download_thread = Thread(target=self.download_images, args=(article_number, save_path))
        download_thread.start()
    
    def download_images(self, article_number, save_path):
        try:
            url = f"https://adult.contents.fc2.com/article/{article_number}/"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            cookies = {
                'wei6H': '1',
            }
            
            self.log_message(f"正在訪問: {url}")
            self.update_progress(10)
            
            response = requests.get(url, headers=headers, cookies=cookies)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 獲取標題
            title_tag = soup.find('title')
            if title_tag:
                title_text = title_tag.get_text().strip()
                title_text = re.sub(r'[\\/*?:"<>|]', '', title_text)
                title_text = re.split(r'FC2-PPV', title_text)[0].strip()
                title_text = title_text[:70].strip()
            else:
                title_text = "NoTitle"
            
            # 創建目錄
            article_id = article_number
            directory_name = f"FC2-PPV-{article_id} {title_text}"
            directory_name = re.sub(r'[\\/*?:"<>|]', '', directory_name)
            directory_name = directory_name[:100].strip()
            
            full_path = os.path.join(save_path, directory_name)
            os.makedirs(full_path, exist_ok=True)
            
            self.log_message(f"創建目錄: {full_path}")
            self.update_progress(20)
            
            # 下載封面圖片
            thumb_div = soup.find('div', class_='items_article_MainitemThumb')
            if thumb_div:
                img_tag = thumb_div.find('img')
                if img_tag and 'src' in img_tag.attrs:
                    img_url = img_tag['src']
                    
                    if img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    
                    self.log_message(f"正在下載封面圖片: {img_url}")
                    
                    try:
                        img_filename = os.path.basename(img_url)[:50].strip()
                        img_filename = re.sub(r'[\\/*?:"<>|]', '', img_filename)
                        img_filepath = os.path.join(full_path, img_filename)
                        
                        urllib.request.urlretrieve(img_url, img_filepath)
                        self.log_message(f"封面圖片下載完成: {img_filename}")
                    except Exception as e:
                        self.log_message(f"封面圖片下載失敗: {e}")
            
            self.update_progress(50)
            
            # 下載預覽圖片
            sample_images_area = soup.find('ul', class_='items_article_SampleImagesArea')
            if sample_images_area:
                img_tags = sample_images_area.find_all('img')
                total_images = len(img_tags)
                self.log_message(f"找到 {total_images} 張預覽圖片")
                
                for i, img_tag in enumerate(img_tags):
                    if 'src' in img_tag.attrs:
                        img_url = img_tag['src']
                        
                        if img_url.startswith('//'):
                            img_url = 'https:' + img_url
                        
                        self.log_message(f"正在下載預覽圖片 ({i+1}/{total_images}): {img_url}")
                        
                        try:
                            img_filename = os.path.basename(img_url)[:50].strip()
                            img_filename = re.sub(r'[\\/*?:"<>|]', '', img_filename)
                            img_filepath = os.path.join(full_path, img_filename)
                            
                            urllib.request.urlretrieve(img_url, img_filepath)
                            self.log_message(f"預覽圖片下載完成: {img_filename}")
                        except Exception as e:
                            self.log_message(f"預覽圖片下載失敗: {e}")
                        
                        # 更新進度條
                        progress = 50 + (i + 1) * 50 / total_images
                        self.update_progress(progress)
            
            self.log_message("所有圖片下載完成！")
            self.update_progress(100)
            messagebox.showinfo("完成", "圖片下載完成！")
            
        except Exception as e:
            self.log_message(f"發生錯誤: {str(e)}")
            messagebox.showerror("錯誤", f"下載過程中發生錯誤: {str(e)}")
        finally:
            self.download_btn.config(state='normal')

if __name__ == "__main__":
    root = tk.Tk()
    app = FC2PPVDownloader(root)
    root.mainloop()
