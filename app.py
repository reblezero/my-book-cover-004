import streamlit as st
import os
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
from fpdf import FPDF
import urllib.parse
from datetime import datetime

# 설정값
TARGET_HEIGHT_MM = 30
PAGE_WIDTH_MM = 210
MARGIN_MM = 10
DPI = 300
GAP_MM = 1 

def get_high_res_cover(book_title):
    try:
        encoded_title = urllib.parse.quote(book_title)
        url = f"https://www.aladin.co.kr/search/wsearchresult.aspx?SearchTarget=All&SearchWord={encoded_title}"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        boxes = soup.select("div.ss_book_box")
        img_src = None
        for box in boxes:
            box_text = box.get_text()
            if any(x in box_text for x in ["[알라딘 굿즈]", "[음반]", "머그", "[블루레이]"]): continue
            img_tag = box.select_one("img.i_cover") or box.select_one("img.front_cover")
            if img_tag and img_tag.has_attr('src'):
                img_src = img_tag['src']
                break
        if not img_src: return None
        high_res_src = img_src.replace('coversum', 'cover500').replace('cover200', 'cover500').replace('cover150', 'cover500')
        img_res = requests.get(high_res_src, headers=headers, timeout=10)
        img = Image.open(BytesIO(img_res.content))
        target_height_px = int((TARGET_HEIGHT_MM / 25.4) * DPI)
        width_ratio = target_height_px / img.height
        target_width_px = int(img.width * width_ratio)
        return img.resize((target_width_px, target_height_px), Image.Resampling.LANCZOS)
    except: return None

st.set_page_config(page_title="알라딘 표지 메이커", page_icon="📚")
st.title("📚 알라딘 책 표지 자동 수집기")
titles_input = st.text_area("책 제목을 한 줄에 하나씩 입력하세요:", height=150)

if st.button("🚀 PDF 만들기 시작!"):
    titles = [t.strip() for t in titles_input.split('\n') if t.strip()]
    if not titles:
        st.warning("책 제목을 입력해주세요!")
    else:
        images = []
        progress_bar = st.progress(0)
        for i, t in enumerate(titles):
            img = get_high_res_cover(t)
            if img: images.append(img)
            progress_bar.progress((i + 1) / len(titles))
        
        if images:
            pdf = FPDF()
            pdf.add_page()
            x, y = MARGIN_MM, MARGIN_MM
            for i, img in enumerate(images):
                temp_path = f"temp_{i}.png"
                img.save(temp_path)
                w_mm = (img.width / DPI) * 25.4
                if x + w_mm > PAGE_WIDTH_MM - MARGIN_MM:
                    x = MARGIN_MM
                    y += TARGET_HEIGHT_MM + GAP_MM
                if y + TARGET_HEIGHT_MM > 280:
                    pdf.add_page()
                    y, x = MARGIN_MM, MARGIN_MM
                pdf.image(temp_path, x=x, y=y, h=TARGET_HEIGHT_MM)
                x += w_mm + GAP_MM
                os.remove(temp_path)
            
           pdf_bytes = pdf.output()
            st.download_button(label="📥 완성된 PDF 다운로드", data=pdf_bytes, file_name=f"covers_{datetime.now().strftime('%Y%m%d')}.pdf", mime="application/pdf")
        else:
            st.error("표지를 찾지 못했습니다.")