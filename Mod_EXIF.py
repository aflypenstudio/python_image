# liberary Need install before use
# pip install piexif

# 功能說明
#1.標題和主旨為檔案名程(去除尾部數字)
#2.EXIF未設定過，會自動初始化
#3.版權預設為版權所有
#4.作者piexif.ImageIFD.Artist 可以自行修改
#5.關鍵字piexif.ImageIFD.XPKeywords 在Windows 顯示標籤 ; 分隔 可以自行修改
#6.備註piexif.ImageIFD.XPComment 可以自行修改

import os
import re
from PIL import Image
import piexif

def remove_digits(filename):
    return re.sub(r'\d', '', filename)

def update_exif(image_path):
    # 讀取圖片
    img = Image.open(image_path)

    # 構建新的 EXIF 資訊
    try:
        exif_dict = piexif.load(img.info.get('exif', b''))
    except Exception as e:
        print(f"無法讀取 {image_path} 的 EXIF 資訊: {e}")
        exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}}

    # 檔名去掉數字
    filename = os.path.splitext(os.path.basename(image_path))[0]
    cleaned_name = remove_digits(filename)

    # 設定 EXIF 資訊（將字串轉換為 bytes 格式）
    exif_dict['0th'][piexif.ImageIFD.ImageDescription] = cleaned_name.encode('utf-8')
    exif_dict['0th'][piexif.ImageIFD.Artist] = "Editor".encode('utf-8')
    exif_dict['0th'][piexif.ImageIFD.Copyright] = "版權所有".encode('utf-8')

    # 使用 UTF-16LE 編碼 XP 欄位
    exif_dict['0th'][piexif.ImageIFD.XPTitle] = cleaned_name.encode('utf-16le')
    exif_dict['0th'][piexif.ImageIFD.XPSubject] = cleaned_name.encode('utf-16le')
    exif_dict['0th'][piexif.ImageIFD.XPKeywords] = "AI;創作".encode('utf-16le')
    exif_dict['0th'][piexif.ImageIFD.XPComment] = "這是備註".encode('utf-16le')
    
    # 轉換 EXIF 資訊為 bytes 並寫入圖片
    try:
        exif_bytes = piexif.dump(exif_dict)
        img.save(image_path, "jpeg", exif=exif_bytes)
        print(f"已更新 EXIF 資訊: {image_path}")
    except Exception as e:
        print(f"無法處理 {image_path}: {e}")
        return
    
    # 顯示更新後的 EXIF 資訊
    updated_img = Image.open(image_path)
    try:
        updated_exif = piexif.load(updated_img.info.get('exif', b''))
    except Exception as e:
        print(f"無法讀取更新後的 EXIF 資訊: {e}")
        return
    
    # 格式化顯示 EXIF 資訊
    print(f"顯示 {image_path} 的更新後 EXIF 資訊：")
    for ifd_name in updated_exif:
        if updated_exif[ifd_name] is not None:  # 確認 EXIF 欄位非 None
            for tag, value in updated_exif[ifd_name].items():
                tag_name = piexif.TAGS[ifd_name].get(tag, {}).get('name', tag)
                if isinstance(value, bytes):
                    try:
                        value = value.decode('utf-16le')
                    except UnicodeDecodeError:
                        value = value.decode('utf-8', errors='ignore')
                elif isinstance(value, tuple):
                    value = f"Tuple data (length {len(value)})"  # 或視情況省略
                print(f"{tag_name}: {value}")

def process_directory(directory_path):
    # 遍歷指定目錄下的所有文件
    for root, _, files in os.walk(directory_path):
        for file in files:
            # 判斷是否為 JPEG 格式的圖片
            if file.lower().endswith(('.jpg', '.jpeg')):
                image_path = os.path.join(root, file)
                try:
                    update_exif(image_path)
                except Exception as e:
                    print(f"無法處理 {image_path}: {e}")

# 執行腳本
directory_path = r"D:\AI_Work\Copilot_待處理"
process_directory(directory_path)
