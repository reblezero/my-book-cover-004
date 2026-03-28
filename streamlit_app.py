import streamlit as st
import os
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
from fpdf import FPDF
import urllib.parse
import warnings
from datetime import datetime

warnings.filterwarnings('ignore')

# --- 설정값 ---
TARGET_HEIGHT_MM = 30
PAGE_WIDTH_MM = 210
MARGIN_MM = 10
DPI = 300
GAP_MM = 1 

# --- 핵심 기능: 알라딘에서 고화질 표지 가져오기 ---
def get_high_res_cover(book_title):
    try:
        encoded_title = urllib.parse.quote(book_title)
        url = f"https://www.aladin.co.kr/search/wsearchresult.aspx?SearchTarget=All&SearchWord={encoded_title}"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://www.aladin.co.kr/"
        }
        res = requests.get(url, headers=headers, verify=False, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        boxes = soup.select("div.ss_book_box")
        img_src = None
        for box in boxes:
            box_text = box.get_text()
            if any(x in box_text for x in ["[알라딘 굿즈]", "[음반]", "머그", "[블루레이]"]):
                continue 
            img_tag = box.select_one("img.i_cover") or box.select_one("img.front_cover")
            if img_tag and img_tag.has_attr('src'):
                img_src = img_tag['src']
                break
        if not img_src: return None
        high_res_src = img_src.replace('coversum', 'cover500').replace('cover200', 'cover500').replace('cover150', 'cover500')
        img_res = requests.get(high_res_src, headers=headers, verify=False, timeout=10)
        img = Image.open(BytesIO(img_res.content))
        target_height_px = int((TARGET_HEIGHT_MM / 25.4) * DPI)
        width_ratio = target_height_px / img.height
        target_width_px = int(img.width * width_ratio)
        return img.resize((target_width_px, target_height_px), Image.Resampling.LANCZOS)
    except Exception:
        return None

# --- 웹 화면(UI) 구성 ---
st.set_page_config(page_title="알라딘 표지 메이커", page_icon="📚")
st.title("📚 알라딘 책 표지 자동 수집기")
st.markdown("책 제목을 입력하면 세로 **3cm**에 맞춰진 인쇄용 PDF를 만들어줍니다!")

titles_input = st.text_area(
    "책 제목을 한 줄에 하나씩 입력하세요:", 
    height=150, 
    placeholder="구름 사람들\n파친코\n불편한 편의점"
)

if st.button("🚀 PDF 만들기 시작!"):
    titles = [t.strip() for t in titles_input.split('\n') if t.strip()]
    if not titles:
        st.warning("책 제목을 먼저 입력해주세요!")
    else:
        images = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        for i, t in enumerate(titles):
            status_text.text(f"'{t}' 표지 찾는 중... ({i+1}/{len(titles)})")
            img = get_high_res_cover(t)
            if img: images.append(img)
            else: st.toast(f"'{t}' 표지 찾기 실패 ❌")
            progress_bar.progress((i + 1) / len(titles))
            
        status_text.text("이미지 조합 중...")

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
            
            # --- [수정 완료된 출력 부분] ---
            pdf_output = pdf.output()
            
            now = datetime.now()
            time_str = now.strftime("%Y%m%d_%H%M%S")
            filename = f"covers_{time_str}.pdf"
            
            st.success("✅ PDF 생성이 완료되었습니다!")
            st.download_button(
                label="📥 완성된 PDF 다운로드",
                data=pdf_output,
                file_name=filename,
                mime="application/pdf"
            )
        else:
            st.error("저장할 표지가 없습니다. 제목을 확인해주세요.")