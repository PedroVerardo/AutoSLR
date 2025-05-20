import re
import fitz
from statistics import mode
from typing import List, Dict, Tuple, Optional, Union, Any
import numpy as np
import logging
from roman import fromRoman, InvalidRomanNumeralError

'''
Considerations:
- The regex could not be super generic
- The introduction section probably in the first page
- In some cases the section title could be in bold or something similar
- The sections are always in order, if some number is in the title
- Always the section going to be between \\n
- A number of trashold could be used for the quantity of words in the section
- The letters of the section title are bigger in the most of the time
- The first letter of the section probally is a capital letter
- Could be implemented some regex to remove tables, images for descriptions
    - Ex: figure 1.1: Some description, table 1.1: Some description
- Could store the probaly sequence of section titles
- Is difficult to find three or more sections in the same page
- probably do not have ponctuation in the section title
- You could remove all figure 1. of the text
'''

logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.StreamHandler()
    ]
)

logging.basicConfig(
    level=logging.WARNING,
    handlers=[
        logging.StreamHandler()
    ]
)

def extract_span_formatting(span):
    """Extract formatting details from a text span."""
    span_text = span["text"]
    if not span_text.strip():
        return None  # Skip empty spans
    
    return {
        "text": span_text,
        "font_size": span["size"],
        "is_bold": PDFHandler.is_bold_by_metrics(span),
        "is_italic": "italic" in span["font"].lower(),
        "font_name": span["font"],
        "font_color": span.get("color", 0),
        "is_superscript": span.get("superscript", False),
        "is_subscript": span.get("subscript", False),
    }

class PDFHandler:
    regex_patterns = {
        "non_ascii": r"[\\x00-\\x08\\x0B-\\x1F\\x7F-\\x9F\\xA0]",
        "unicode_spaces": r"[\\u00A0\\u2000-\\u200F\\u2028\\u2029\\u202F\\u3000]",
        "references": r"^\s*[Rr][Ee][Ff][Ee][Rr][Ee][Nn][Cc][Ee][Ss](?:\s*|\s+[^\n<]+)\n",
        "abstract": r"^\s*[Aa][Bb][Ss][Tt][Rr][Aa][Cc][Tt](?:\s*|\s+[^\n<]+)\n",
        "numeric_point_section": r"^\s*(\d)\.\s+([A-Z][^<]+)\n",
        "rome_point_section": r"^\s*([IVX]+)\.\s+([A-Z][^<]+)\n",
        "numeric_section": r"^\s*(\d)\s+([A-Z][^<]+)\n",
        "table_description": r"(TABLE|Table|table)\s*\d+\.[\s\S]+?\n",
        "citation1": r"^\[(\d)\]\s*([^\[]+)\n",
        "bold_tag": r"<--bold-->",
        "italic_tag": r"<--italic-->",
        "size_tag": r"<--size=(\d+(\.\d+)?)-->",
        "page_start_tag": r"<--page_start:(\d+)-->",
        "page_end_tag": r"<--page_end:(\d+)-->",
        "image_tag": r"<--image width=(\d+(\.\d+)?) height=(\d+(\.\d+)?)-->",
    }
    
    normal_article_words = [
        "abstract", "introduction", "background", "related work", "conclusion"
    ]

    @staticmethod
    def try_open(pdf_path: str):
        try:
            doc = fitz.open(pdf_path)
            return doc
        except FileNotFoundError:
            print(f"File not found: {pdf_path}")
            return None
        except Exception as e:
            print(f"An error occurred: {e} in {__file__} ")
            return None

    @staticmethod
    def is_bold_by_metrics(span):
        """Determine if text is bold based on character width/height ratio and font information"""
        bold_patterns = [
            "bold", "heavy", "black", "semibold", "demi", "medium",
            "thick", "wide", "expanded"
        ]
        
        if any(pattern in span["font"].lower() for pattern in bold_patterns):
            return True
            
        weight = span.get("font-weight", 0)
        if weight >= 600:  # CSS font-weight: 600+ is considered bold
            return True
            
        return False

    @staticmethod
    def get_metadata(doc: fitz.Document):
        """This function extracts metadata from a PDF file.

        Args:
            doc (fitz.Document): The PDF document object.

        Returns:
            dict: A dictionary containing the metadata of the PDF file.
        """
        try:
            metadata = doc.metadata
            return metadata
        
        except Exception as e:
            print(f"An error occurred: {e} in {__file__} ")
            return None

    @staticmethod
    def find_first_pattern_position(text: str, section_pattern: str) -> int:
        """Find the first occurrence of a section pattern in the text.
        
        Args:
            text (str): Tagged text from tagged_extraction
            section_pattern (str): Regex pattern to match sections
            
        Returns:
            int: Position of the first occurrence or -1 if not found
        """
        match = re.search(section_pattern, text)
        if match:
            return match.start()
        logging.warning("Pattern not found in text.")
        return -1  

    @staticmethod
    def trim_before_position(text: str, position: int, size: int) -> str:
        """Remove all text before the introduction section.
        
        Args:
            text (str): Tagged text from tagged_extraction
            
        Returns:
            str: Text starting from introduction or abstract
        """
        if position > 0 and position < size:
            return text[position:]

        logging.warning("No valid position found for trimming.")
        return text

    @staticmethod
    def find_pdf_topics_outline(doc: fitz.Document, words: Optional[List[str]] = None) -> List[Dict[str, Union[str, int]]]:
        """Extracts the outline information (topics) from a PDF document's table of contents (TOC).
        The function uses a voting mechanism to determine the most likely depth level for section titles.

        Args:
            doc (fitz.Document): The PDF document object.
            words (Optional[List[str]]): List of keywords to identify relevant sections. Defaults to common section titles.

        Returns:
            List[Dict[str, Union[str, int]]]: A list of dictionaries containing section titles and page numbers.
        """
        if words is None:
            words = ["abstract", "introduction", "background", "related work", "conclusion"]

        outlines = doc.get_toc() 
        if not outlines:
            logging.warning("No table of contents found in the document.")
            return []

        depth_voting = np.zeros(20, dtype=np.int16)
        information_by_depth = {depth: [] for depth in range(20)}

        for outline in outlines:
            depth = outline[0]
            title = outline[1]
            page_number = outline[2]

            if any(word in title.lower() for word in words):
                depth_voting[depth] += 1

            information_by_depth[depth].append({
                "title": title,
                "page_number": page_number
            })

        argmax_depth = depth_voting.argmax()
        if argmax_depth == 0:
            logging.warning("No valid depth found for section titles. Return default depth 1.")
            return information_by_depth[1]
        
        logging.info(f"Most common depth for section titles: {argmax_depth}")
        for elem in information_by_depth[argmax_depth]:
            logging.info(f"Title: {elem['title']}, Page: {elem['page_number']}")

        return information_by_depth[argmax_depth]
    
    @staticmethod
    def simple_extraction(doc: fitz.Document) -> dict[int, str] | None:
        """This function extracts text from a PDF file and returns the text along with the number of pages.

        Args:
            doc (fitz.Document): The PDF document object

        Returns:
            tuple[str, int]: The text inside the pdf(without any cleaning) and page count
        """
        try:
            text = ""
            total_pages = 0
            for idx, page in enumerate(doc):
                text += f"<--page_{idx+1}-->"
                text +=  page.get_text()
                total_pages += 1
            return text, total_pages

        except Exception as e:
            print(f"An error occurred: {e} in {__file__} ")
            return None

    @staticmethod
    def tagged_text_extraction(doc: fitz.Document) -> str:
        """Extracts tagged text from a PDF document, enriching with format information.

        This enhanced method extracts text while preserving formatting information such as:
        - Font size
        - Bold formatting
        - Page numbers
        - Image dimensions

        Args:
            doc (fitz.Document): The PDF document object.

        Returns:
            str: Text with XML-style tags containing formatting information.
        """
        try:
            text = ""
            
            for page_num, page in enumerate(doc):
                text += f"<--page_start:{page_num+1}-->\n"
                
                blocks = page.get_text("dict")["blocks"]
                for block_num, block in enumerate(blocks):

                    if block.get("type") == 1:  # Type 1 is image
                        img_width = block.get("width", 0)
                        img_height = block.get("height", 0)
                        text += f"<--image width={img_width:.1f} height={img_height:.1f}-->\n"
                        continue
                        
                    if "lines" not in block:
                        continue
                    
                    for line in block["lines"]:
                        line_text = ""
                        prev_span = None
                        
                        tags = []
                        line_font_sizes = []
                        line_is_bold = True

                        for span in line["spans"]:
                            mod = extract_span_formatting(span)
                            if mod is None:
                                continue
                            line_font_sizes.append(mod["font_size"])
                            if not mod["is_bold"]:
                                line_is_bold = False
                            line_text += mod["text"]

                        if line_font_sizes:
                            most_common_size = mode(line_font_sizes)
                            size_tag = f"<--size={most_common_size:.1f}-->"
                            tags.append(size_tag)

                        if line_is_bold:
                            tags.append("<--bold-->")

                        text += line_text + "".join(tags) + "\n"

                    text += "\n"
                text += f"<--page_end:{page_num+1}-->\n\n"
            return text, page_num+1

        except Exception as e:
            logging.error(f"Error in tagged_text_extraction: {e}")
            return None
    
    @staticmethod
    def convert_rome_to_numeric(rome: str) -> int:
        """Convert a Roman numeral string to an integer.

        Args:
            rome (str): The Roman numeral string.

        Returns:
            int: The integer value of the Roman numeral.
        """
        try:
            return fromRoman(rome.upper())
        except InvalidRomanNumeralError as irne:
            logging.error(f"Error converting Roman numeral: {irne}")
            return int(rome)

    @staticmethod
    def extract_section_title_and_text(text: str, pattern: str, isTextTagged: bool) -> List[Dict[str, Union[str, int]]]:
        page_number = 0
        match_count = 0
        for line in text.split("\n"):
            page_match = re.search(PDFHandler.regex_patterns["page_start_tag"], line)
            match = re.search(pattern, line)
            if page_match:
                page_number = int(page_match.group(1))
            
            if match and match.group(1) and match.group(2):
                section_number = match.group(1)
                section_title = match.group(2).strip()
                section_position = match.start()
            elif match and match.group(1) and not match.group(2):
                section_number = match_count
                section_title = match.group(1)

if __name__ == "__main__":
    path = "/home/pedro/Documents/Rag_test/grpc/papers_pdf/ACM/muhlbauer2023_icse.pdf"
    pattern = "numeric_section"
    tagged = True
    
    doc = PDFHandler.try_open(path)
    if doc == None:
        print("error opening the pdf")
        exit(1)

    topics = PDFHandler.find_pdf_topics_outline(doc)
    if topics == None:
        print("do not found outline")
    
    result, numberOfPages = PDFHandler.tagged_text_extraction(doc)
        
    if result == None:
        tagged = False
        print("error during the tagged extraction")
        result = PDFHandler.simple_extraction(doc)
    
    print(result)
    print("number of pages: ", numberOfPages)

    if result == None:
        print("error during the simple extraction")
        exit(1)
    
