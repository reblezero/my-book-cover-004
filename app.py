import streamlit as st
from io import BytesIO

# 1. 페이지 설정 (가장 상단에 위치해야 함)
st.set_page_config(page_title="나만의 책 표지 만들기", layout="centered")

def main():
    st.title("📚 AI 책 표지 제작 도구")
    st.write("이미지를 생성하고 PDF로 변환하여 다운로드하세요.")

    # 사이드바 설정
    st.sidebar.header("설정")
    user_input = st.sidebar.text_input("표지에 넣을 제목", placeholder="여기에 제목 입력...")
    
    # 세션 상태 초기화 (데이터가 없을 때 에러 방지)
    if 'pdf_data' not in st.session_state:
        st.session_state.pdf_data = None

    # --- [이미지 생성 및 PDF 변환 로직 - 예시] ---
    # 실제 PDF 생성 라이브러리(reportlab 등)가 있다면 여기서 호출하십시오.
    if st.button("🎨 PDF 생성하기"):
        with st.spinner("PDF를 굽는 중입니다..."):
            try:
                # 가상의 PDF 데이터 생성 (실제 구현 시 이 부분을 PDF 생성 코드로 교체)
                # 예시: 임시 바이트 데이터를 PDF 형식처럼 생성
                dummy_data = BytesIO()
                dummy_data.write(b"%PDF-1.4\n1 0 obj\n<< /Title (My Book) >>\nendobj\n") 
                st.session_state.pdf_data = dummy_data.getvalue()
                
                st.success("✅ PDF가 성공적으로 생성되었습니다!")
            except Exception as e:
                st.error(f"생성 중 오류 발생: {e}")

    st.divider()

    # --- [에러 방지용 다운로드 버튼 구역] ---
    st.subheader("📥 다운로드")

    # 데이터가 존재할 때만 버튼을 노출하여 StreamlitAPIException을 원천 봉쇄합니다.
    if st.session_state.pdf_data is not None:
        try:
            st.download_button(
                label="📥 완성된 PDF 다운로드",
                data=st.session_state.pdf_data,
                file_name=f"{user_input if user_input else 'book_cover'}.pdf",
                mime="application/pdf"
            )
            st.info("버튼을 클릭하여 내 컴퓨터에 저장하세요.")
        except Exception as e:
            st.error(f"다운로드 버튼 준비 중 오류가 발생했습니다: {e}")
    else:
        # 데이터가 없을 때 사용자에게 명확한 가이드를 줍니다.
        st.warning("위의 'PDF 생성하기' 버튼을 먼저 눌러주셔야 다운로드가 가능합니다.")
        st.button("📥 완성된 PDF 다운로드 (비활성화)", disabled=True)

if __name__ == "__main__":
    main()