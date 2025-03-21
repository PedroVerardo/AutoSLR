import fitz
import re
import logging
from src.regex_pattern import RegexPattern
import time

logger = logging.getLogger(__name__)

# def extract_text_with_metadata(pdf_path):
#     doc = fitz.open(pdf_path)
#     extracted_text = []
    
#     result = []
#     patterns = RegexPattern()

#     for page_number, page in enumerate(doc, start=1):
#         blocks = page.get_text("dict")["blocks"]
#         for block in blocks:
#             if "lines" in block:
#                 for line in block["lines"]:
#                     for span in line["spans"]:
#                         text = span["text"].strip()
#                         non_ascii = patterns.get_pattern("non_ascii")
#                         clean_text = re.sub(non_ascii, "", text)
#                         unicode_spaces = patterns.get_pattern("unicode_spaces")
#                         clean_text = re.sub(unicode_spaces, " ", clean_text)
#                         font = span["font"]
#                         if "bold" in font.lower():
#                             result.append((clean_text))
#                         size = int(span["size"])
                        
#                         if text: 
#                             extracted_text.append(f"{text} <font:{font}> <size:{size}>")
    
#     return result

def extract_text(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    text = ''
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

def extract_sections(pdf_text: str, section_pattern: str):

    patterns = RegexPattern()
    non_ascii = patterns.get_pattern("non_ascii")
    if not isinstance(pdf_text, str):
        pdf_text = str(pdf_text)

    clean_text = re.sub(non_ascii, "", pdf_text)
    logging.info("Time to clean text: %s", time.time())

    # "pattern": "\\n\\s*[Rr][Ee][Ff][Ee][Rr][Ee][Nn][Cc][Ee][Ss]\\s*\\n",
    reference_pattern = patterns.get_pattern("references")
    split_text = re.split(reference_pattern, clean_text, flags=re.IGNORECASE, maxsplit=1)
    logging.info("Time to split reference: %s", time.time())

    if len(split_text) == 2:
        clean_text, reference = split_text
    else:
        clean_text, reference = split_text[0], ""


    # table_description_pattern = patterns.get_pattern("table_description")
    # clean_text = re.sub(table_description_pattern, "", clean_text)

    #TODO: Implement reference extraction

    # reference_dict = {}
    # citation_pattern = patterns.get_pattern("citation1")

    # matches = re.findall(citation_pattern, reference, re.DOTALL)
    # for match in matches:
    #     reference_dict[int(match[0])] = match[1].strip()

    document_section_pattern = patterns.get_pattern(section_pattern)
    matches = list(re.finditer(document_section_pattern, clean_text, re.MULTILINE))
    logging.info("Time to split sections: %s", time.time())

    segments = []
    for i in range(len(matches)):
        start = matches[i].end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(clean_text)
        segment_text = clean_text[start:end].strip()
        segments.append((matches[i].group().strip(), segment_text))
    logging.info("Time to extract segments: %s", time.time())

    logger.info("DOCUMENT SECTION DEBUG:")
    for i in segments:
        logger.info(re.sub(r"\n", " ", i[0]))

    return segments


if __name__ == "__main__":
    pdf_path = "jailmaReviewPdf/jamshidi2017b.pdf"
    extracted_text = extract_text(pdf_path)

    start_time = time.time()
    segments = extract_sections(extracted_text, "rome_point_section")
    end_time = time.time()
    logger.info("ExtractText function took %s seconds", end_time - start_time)

    # with open("output.json", "w") as f:
    #     json.dump(segments, f, indent=4)


    
    
    