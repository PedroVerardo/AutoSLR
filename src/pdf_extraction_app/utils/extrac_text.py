import fitz
import re
import logging
from .regex_pattern import RegexPattern
from collections import OrderedDict


def extract_text_with_metadata(pdf_path, section_pattern):
    doc = fitz.open(pdf_path)
    sections = OrderedDict()
    current_section = None
    patterns = RegexPattern()
    non_ascii = patterns.get_pattern("non_ascii")
    unicode_spaces = patterns.get_pattern("unicode_spaces")
    number_text = patterns.get_pattern(section_pattern)
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text_blocks = page.get_text("dict")["blocks"]
        
        for block in text_blocks:
            if "lines" not in block:
                continue
                
            for line in block["lines"]:
                is_bold = any("bold" in span["font"].lower() for span in line["spans"])
                line_text = " ".join(span["text"] for span in line["spans"]).strip()
                
                clean_text = re.sub(non_ascii, "", line_text)
                clean_text = re.sub(unicode_spaces, " ", clean_text)
                
                if is_bold and re.search(number_text, clean_text):
                    if current_section and len(sections[current_section]) < 350:
                        del sections[current_section]
                    
                    current_section = clean_text
                    sections[current_section] = ""
                    
                elif current_section is not None:
                    sections[current_section] += clean_text + "\n"
    
    result = [{"title": title, "content": content.strip()} for title, content in sections.items()]
    
    doc.close()
    return result

def extract_text(pdf_path):
    doc = fitz.open(pdf_path)
    text = ''
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

def ExtractText(pdf_text: str, section_pattern: str):

    patterns = RegexPattern()

    non_ascii = patterns.get_pattern("non_ascii")
    clean_text = re.sub(non_ascii, "", pdf_text)

    # "pattern": "\\n\\s*[Rr][Ee][Ff][Ee][Rr][Ee][Nn][Cc][Ee][Ss]\\s*\\n",
    reference_pattern = patterns.get_pattern("references")
    clean_text, reference = re.split(reference_pattern, clean_text, flags=re.IGNORECASE, maxsplit=1)

    table_description_pattern = patterns.get_pattern("table_description")
    clean_text = re.sub(table_description_pattern, "", clean_text)

    reference_dict = {}
    citation_pattern = patterns.get_pattern("citation1")

    matches = re.findall(citation_pattern, reference, re.DOTALL)
    for match in matches:
        reference_dict[int(match[0])] = match[1].strip()

    document_section_pattern = patterns.get_pattern(section_pattern)
    matches = list(re.finditer(document_section_pattern, clean_text, re.MULTILINE))

    segments = []
    for i in range(len(matches)):
        start = matches[i].end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(clean_text)
        segment_text = clean_text[start:end].strip()
        segments.append((matches[i].group().strip(), segment_text))


if __name__ == "__main__":
    pdf_path = "/home/PUC/Documentos/AutoSLR/papers_pdf/ScienceDirect/lesoil2023.pdf"
    extracted_text = extract_text_with_metadata(pdf_path, "numeric_point_section")
    #extract_text(pdf_path, debug=True)

    print(extracted_text)

    # "pattern": "(?<=\\n)(\\d+)\\.\\s*[A-Z][^\\n]+\\n"
    # ExtractText(extracted_text, "numeric_section")
    #print( "bold" in "CharisSIL-Bold".lower())