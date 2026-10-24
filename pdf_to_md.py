import streamlit as st
import pdfplumber
import io

st.set_page_config(page_title="PDF to Markdown 변환기", layout="wide")

st.title("📄 소방시설법령/해설서 PDF ➡️ Markdown 변환기")
st.write("대용량 PDF 문서를 마크다운(.md) 텍스트로 추출합니다.")

uploaded_file = st.file_uploader("PDF 파일을 업로드하세요", type=["pdf"])

if uploaded_file is not None:
    st.success(f"파일명: {uploaded_file.name}")
    
    if st.button("Markdown 변환 시작"):
        markdown_text = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Streamlit 메모리 관리를 위해 BytesIO 사용
        with pdfplumber.open(io.BytesIO(uploaded_file.read())) as pdf:
            total_pages = len(pdf.pages)
            st.info(f"총 {total_pages} 페이지 감지됨")
            
            for i, page in enumerate(pdf.pages):
                # 진행률 표시
                progress = (i + 1) / total_pages
                progress_bar.progress(progress)
                status_text.text(f"처리 중: {i+1} / {total_pages} 페이지")
                
                # 텍스트 추출
                text = page.extract_text()
                if text:
                    markdown_text.append(f"\n\n## [Page {i+1}]\n\n")
                    markdown_text.append(text)
                
                # 표(Table) 추출
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
