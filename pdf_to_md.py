import pdfplumber
import os

def pdf_to_markdown(pdf_path, output_md_path):
    print(f"'{pdf_path}' 변환을 시작합니다...")
    markdown_content = []

    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        print(f"총 페이지 수: {total_pages}페이지")

        for i, page in enumerate(pdf.pages):
            print(f"진행 중: {i+1} / {total_pages} 페이지 변환 중...", end="\r")

            # 텍스트 추출
            text = page.extract_text()
            if text:
                markdown_content.append(f"\n\n## [Page {i+1}]\n\n")
                markdown_content.append(text)

            # 표(Table) 추출
            tables = page.extract_tables()
            if tables:
                for table in tables:
                    markdown_content.append("\n\n")
                    # 마크다운 테이블 포맷팅
                    for row_idx, row in enumerate(table):
                        cleaned_row = [str(cell).strip().replace('\n', ' ') if cell else "" for cell in row]
                        markdown_content.append("| " + " | ".join(cleaned_row) + " |")
                        if row_idx == 0:
                            markdown_content.append("| " + " | ".join(["---"] * len(row)) + " |")
                    markdown_content.append("\n")

    # 파일로 저장
    with open(output_md_path, "w", encoding="utf-8") as f:
        f.write("".join(markdown_content))

    print(f"\n변환 완료! 저장된 파일: {output_md_path}")

if __name__ == "__main__":
    # 변환할 PDF 파일 경로 입력 (예: '점검실무행정.pdf')
    pdf_file = "점검실무행정.pdf" 
    output_file = "점검실무행정_변환본.md"

    if os.path.exists(pdf_file):
        pdf_to_markdown(pdf_file, output_file)
    else:
        print(f"오류: '{pdf_file}' 파일을 찾을 수 없습니다. 파일명을 확인해 주세요.")