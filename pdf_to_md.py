import streamlit as st
import fitz  # PyMuPDF (설치 명령어: pip install PyMuPDF)
import io

# OCR용 라이브러리 (선택 사항)
try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

st.set_page_config(page_title="PDF to Markdown 변환기", layout="wide")
st.title("📄 고속 통합 소방 PDF ➡️ Markdown 변환기")
st.write("텍스트 PDF와 스캔본(이미지) PDF를 모두 완벽하게 지원합니다.")

uploaded_file = st.file_uploader("PDF 파일을 업로드하세요", type=["pdf"])

if uploaded_file is not None:
    st.success(f"파일명: {uploaded_file.name}")
    
    if st.button("Markdown 변환 시작"):
        markdown_text = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            pdf_bytes = uploaded_file.read()
            
            # PyMuPDF로 PDF 열기 (별도 외부 프로그램 불필요)
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            total_pages = len(doc)
            st.info(f"총 {total_pages} 페이지 감지됨")
            
            for i in range(total_pages):
                progress = (i + 1) / total_pages
                progress_bar.progress(progress)
                status_text.text(f"처리 중: {i+1} / {total_pages} 페이지")
                
                markdown_text.append(f"\n\n## [Page {i+1}]\n\n")
                
                page = doc[i]
                # 1단계: 네이티브 텍스트 추출 시도
                text = page.get_text("text")
                
                # 2단계: 텍스트가 거의 없거나 빈 페이지(스캔본)인 경우 PyMuPDF 자체 기능으로 이미지 추출 후 OCR 시도
                if (not text or len(text.strip()) < 5) and OCR_AVAILABLE:
                    status_text.text(f"처리 중 (이미지 OCR 판독): {i+1} / {total_pages} 페이지")
                    try:
                        pix = page.get_pixmap(dpi=150)
                        img = Image.open(io.BytesIO(pix.tobytes("png")))
                        text = pytesseract.image_to_string(img, lang='kor+eng')
                    except Exception as ocr_err:
                        text = f"[OCR 판독 오류: {ocr_err}]"
                
                if text:
                    markdown_text.append(text)
                else:
                    markdown_text.append("[텍스트를 추출할 수 없는 페이지입니다.]")
            
            result_md = "".join(markdown_text)
            
            st.success("변환이 완료되었습니다!")
            
            # 다운로드 버튼
            st.download_button(
                label="📥 Markdown 파일 다운로드 (.md)",
                data=result_md,
                file_name=f"{uploaded_file.name.rsplit('.', 1)[0]}.md",
                mime="text/markdown"
            )
            
            # 결과 미리보기 (일부만)
            with st.expander("변환 결과 미리보기 (상위 2,000자)"):
                st.text_area("Preview", value=result_md[:2000], height=300)
                
        except Exception as e:
            st.error(f"변환 중 오류가 발생했습니다: {e}")
