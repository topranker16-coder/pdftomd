import streamlit as st
import pdfplumber
import io
from PIL import Image

# OCR 기능용 라이브러리 예외 처리 (설치되어 있지 않아도 앱이 꺼지지 않도록 방어 코드 추가)
try:
    from pdf2image import convert_from_bytes
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

st.set_page_config(page_title="통합 PDF to Markdown 변환기", layout="wide")

st.title("📄 텍스트/스캔 통합 소방 PDF ➡️ Markdown 변환기")
st.write("드래그 가능한 일반 PDF와 통 이미지(스캔본) PDF를 모두 지원합니다.")

if not OCR_AVAILABLE:
    st.info("💡 안내: 이미지(스캔본) PDF까지 완벽하게 읽으려면 환경에 `pdf2image`와 `pytesseract`(Tesseract-OCR 엔진)가 설치되어 있어야 합니다. 현재는 텍스트 추출 위주로 동작합니다.")

uploaded_file = st.file_uploader("PDF 파일을 업로드하세요", type=["pdf"])

if uploaded_file is not None:
    st.success(f"파일명: {uploaded_file.name}")
    
    if st.button("Markdown 변환 시작"):
        markdown_text = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            pdf_bytes = uploaded_file.read()
            
            # 1. pdf2image를 이용해 미리 전체 페이지를 이미지로 변환 준비 (OCR 대비)
            images = None
            if OCR_AVAILABLE:
                try:
                    images = convert_from_bytes(pdf_bytes)
                except Exception:
                    pass # poppler 미설치 등의 이유로 실패해도 텍스트 추출은 진행되도록 예외 처리

            # 2. pdfplumber로 텍스트 및 표 추출 시작
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                total_pages = len(pdf.pages)
                st.info(f"총 {total_pages} 페이지 감지됨")
                
                for i, page in enumerate(pdf.pages):
                    progress = (i + 1) / total_pages
                    progress_bar.progress(progress)
                    status_text.text(f"처리 중: {i+1} / {total_pages} 페이지")
                    
                    markdown_text.append(f"\n\n## [Page {i+1}]\n\n")
                    
                    # 우선 텍스트 추출 시도
                    text = page.extract_text()
                    
                    # 텍스트가 없거나 빈 페이지(스캔본 이미지)인 경우 -> OCR 엔진 가동
                    if (not text or len(text.strip()) < 5) and OCR_AVAILABLE and images and i < len(images):
                        status_text.text(f"처리 중 (이미지 OCR 판독): {i+1} / {total_pages} 페이지")
                        try:
                            # 한국어와 영어 동시 인식 설정 (kor + eng)
                            text = pytesseract.image_to_string(images[i], lang='kor+eng')
                        except Exception as ocr_err:
                            text = f"[OCR 판독 중 오류 발생: {ocr_err}]"
                    
                    if text:
                        markdown_text.append(text)
                    
                    # 표(Table) 구조 추출 (텍스트 PDF인 경우 정밀 표 유지)
                    tables = page.extract_tables()
                    if tables:
                        for table in tables:
                            markdown_text.append("\n\n")
                            for row_idx, row in enumerate(table):
                                cleaned_row = [str(cell).strip().replace('\n', ' ') if cell else "" for cell in row]
                                markdown_text.append("| " + " | ".join(cleaned_row) + " |")
                                if row_idx == 0:
                                    markdown_text.append("| " + " | ".join(["---"] * len(row)) + " |")
                            markdown_text.append("\n")
            
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
