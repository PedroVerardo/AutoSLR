import fitz
import re
import logging
from regex_pattern import RegexPattern

logger = logging.getLogger(__name__)

def extract_text_with_metadata(pdf_path, section_pattern):
    doc = fitz.open(pdf_path)
    extracted_text = []
    
    result = []
    patterns = RegexPattern()
    non_ascii = patterns.get_pattern("non_ascii")
    unicode_spaces = patterns.get_pattern("unicode_spaces")
    number_text = patterns.get_pattern(section_pattern)


    for _, page in enumerate(doc, start=1):
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:

                    for span in line["spans"]:
                        if "bold" in span["font"].lower():
                            bold = True
                        else:
                            bold = False
                    
                    if bold:

                        line_text = " ".join(span["text"] for span in line["spans"])
                        clean_text = re.sub(non_ascii, "", line_text)
                        clean_text = re.sub(unicode_spaces, " ", clean_text)

                        if re.search(number_text, clean_text):
                            result.append((clean_text))
    
    return result 

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

    with open("output.txt", "w") as f:
            f.write(clean_text)

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

    with open("output.txt", "w") as f:
            f.write(clean_text)

    # Segmenta o texto
    segments = []
    for i in range(len(matches)):
        start = matches[i].end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(clean_text)
        segment_text = clean_text[start:end].strip()
        segments.append((matches[i].group().strip(), segment_text))

    logger.info("Document sections:")
    for i in segments:
        logger.info(re.sub(r"\n", " ", i[0]))


if __name__ == "__main__":
    pdf_path = "pdfs/ANALYSISONTHESTRATEGYANDIMPLEMENTATIONOFDIGITALTECHNOLOGYINTHEXYZCOMPANY.pdf"
    extracted_text = extract_text_with_metadata(pdf_path, "numeric_point_section")

    print(extracted_text)

    # "pattern": "(?<=\\n)(\\d+)\\.\\s*[A-Z][^\\n]+\\n"
    # ExtractText(extracted_text, "numeric_section")