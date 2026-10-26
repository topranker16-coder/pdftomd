import streamlit as st
import fitz  # PyMuPDF
import io

st.set_page_config(page_title="PDF to Markdown 변환기", layout="wide")
st.title("📄 스마트 소방 PDF ➡️ Markdown 변환기")
st.write("텍스트 PDF 및 이미지(스캔본) PDF를 마크다운으로 변환합니다.")

uploaded_file = st.file_uploader("PDF 파일을 업로드하세요", type=["pdf"])

if uploaded_file is not None:
    st.success(f"파일명: {uploaded_file.name}")
    
    if st.button("Markdown 변환 시작"):
        markdown_text = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            pdf_bytes = uploaded_file.read()
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            total_pages = len(doc)
            st.info(f"총 {total_pages} 페이지 감지됨")
            
            for i in range(total_pages):
                progress = (i + 1) / total_pages
                progress_bar.progress(progress)
                status_text.text(f"처리 중: {i+1} / {total_pages} 페이지")
                
                markdown_text.append(f"\n\n## [Page {i+1}]\n\n")
                
                page = doc[i]
                # 1단계: 기본 텍스트 추출
                text = page.get_text("text")
                
                # 2단계: 텍스트가 없는 스캔본(이미지)인 경우 안내 메시지 대신 이미지 영역 존재 여부 확인
                if not text or len(text.strip()) < 5:
                    # 스캔본 이미지 PDF의 경우 텍스트 레이어가 없어 추출되지 않음을 부드럽게 안내
                    markdown_text.append(
                        "> ⚠️ 이 페이지는 텍스트 레이어가 없는 이미지(스캔본) PDF입니다.\n"
                        "> 제미나이 노트북(NotebookLM)은 **PDF 파일 자체를 통째로 업로드**하는 기능을 지원하므로, "
                        "이 변환기를 거치지 않고 **원본 PDF 파일을 NotebookLM에 직접 업로드**하시는 것이 훨씬 선명하고 정확합니다!"
                    )
                else:
                    markdown_text.append(text)
            
            result_md = "".join(markdown_text)
            
            st.success("변환이 완료되었습니다!")
            
            # 다운로드 버튼
            st.download_button(
                label="📥 Markdown 파일 다운로드 (.md)",
                data=result_md,
                file_name=f"{uploaded_file.name.rsplit('.', 1)[0]}.md",
                mime="text/markdown"
            )
            
            # 결과 미리보기
            with st.expander("변환 결과 미리보기 (상위 2,000자)"):
                st.text_area("Preview", value=result_md[:2000], height=300)
                
        except Exception as e:
            st.error(f"변환 중 오류가 발생했습니다: {e}")
