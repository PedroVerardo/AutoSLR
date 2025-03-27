import fitz
import re
import logging
from pdf_extraction_app.utils.regex_pattern import RegexPattern
from collections import OrderedDict


def extract_text_with_metadata(pdf_path, section_pattern):
    
    doc = fitz.open(pdf_path)
    sections = OrderedDict()
    current_section = None
    patterns = RegexPattern()
    non_ascii = patterns.get_pattern("non_ascii")
    unicode_spaces = patterns.get_pattern("unicode_spaces")
    number_text = patterns.get_pattern(section_pattern)
    
    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("dict")["blocks"]
        
        for block in blocks:
            if "lines" not in block:
                continue
                
            for line in block["lines"]:
                is_bold = False
                line_text = ""
                
                for span in line["spans"]:
                    line_text += span["text"] + " "
                    if "bold" in span["font"].lower():
                        is_bold = True
                
                line_text = line_text.strip()
                clean_text = re.sub(non_ascii, "", line_text)
                clean_text = re.sub(unicode_spaces, " ", clean_text)
                
                # Check if this is a section heading
                if is_bold and re.search(number_text, clean_text):
                    current_section = clean_text
                    sections[current_section] = ""
                # Add content to current section if we've found a section
                elif current_section is not None:
                    sections[current_section] += clean_text + "\n"
    
    # Convert to list of dictionaries for easier handling
    result = []
    for title, content in sections.items():
        result.append({
            "title": title,
            "content": content.strip()
        })
        
    doc.close()
    return result

# Usage example:
# sections = extract_text_with_sections("your_document.pdf", "section_pattern")
# for section in sections:
#     print(f"Section: {section['title']}")
#     print(f"Content: {section['content'][:100]}...")  # Print first 100 chars
#     print("-" * 50)

def extract_text(pdf_path):
    doc = fitz.open(pdf_path)
    text = ''
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

def ExtractText(pdf_text: str, section_pattern: str):


    # Limpa o texto extraído
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

    # Segmenta o texto
    segments = []
    for i in range(len(matches)):
        start = matches[i].end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(clean_text)
        segment_text = clean_text[start:end].strip()
        segments.append((matches[i].group().strip(), segment_text))


if __name__ == "__main__":
    pdf_path = "/home/pedro/Documents/Rag_test/grpc/papers_pdf/ScienceDirect/Arcaini2020.pdf"
    extracted_text = extract_text_with_metadata(pdf_path, "numeric_point_section")
    #extract_text(pdf_path, debug=True)

    print(extracted_text)

    # "pattern": "(?<=\\n)(\\d+)\\.\\s*[A-Z][^\\n]+\\n"
    # ExtractText(extracted_text, "numeric_section")
    #print( "bold" in "CharisSIL-Bold".lower())