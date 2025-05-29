import re
import fitz
from statistics import mode
from typing import List, Dict, Tuple, Optional, Union, Any
import numpy as np
import logging
from roman import fromRoman, InvalidRomanNumeralError
from Section import SectionInfo
from collections import defaultdict
import sqlite3
import time

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
- Could be implemented some regex to remove tables, images 
    - Ex: figure 1.1, table 1.1, Figure: 2.1, fig - 5
- Is difficult to find three or more sections in the same page
- probably do not have ponctuation in the section title
'''

logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler("pdf_extraction.log"),
        logging.StreamHandler()
    ]
)

logging.basicConfig(
    level=logging.WARNING,
    handlers=[
        logging.FileHandler("pdf_extraction.log"),
        logging.StreamHandler()
    ]
)

def extract_span_formatting(span):
    """Extract formatting details from a text span."""
    span_text = span["text"]
    if not span_text.strip():
        return None
    
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
        "non_ascii": r"[\x00-\x08\x0B-\x1F\x7F-\x9F\xA0]",
        "unicode_spaces": r"[\u00A0\u2000-\u200F\u2028\u2029\u202F\u3000]",
        "ponctuation": r"[\\u200B-\\u200F\\u2028\\u2029\\u3000]",
        "ponctuation_ASCII": r"[.!\"#$%&'()*+,-./   ;<=>?@[\\]^_`{|}~]",
        "references": r"[Rr][Ee][Ff][Ee][Rr][Ee][Nn][Cc][Ee][Ss]\n",
        "abstract": r"[Aa][Bb][Ss][Tt][Rr][Aa][Cc][Tt](?:\s*\n",
        "introduction": r"[I][Nn][Tt][Rr][Oo][Dd][Uu][Cc][Tt][Ii][Oo][Nn]\n",
        "background": r"^\s*[Bb][Aa][Cc][Kk][Gg][Rr][Oo][Uu][Nn][Dd]\n",
        "related_work": r"^\s*[Rr][Ee][Ll][Aa][Tt][Ee][Dd]\s*[Ww][Oo][Rr][Kk]\n",
        "conclusion": r"^\s*[Cc][Oo][Nn][Cc][Ll][Uu][Ss][Ii][Oo][Nn]\n",
        "figure": r"(?i)\b(?:figure|fig)\.?\s*\d+(?:[-.:]?\d+)?\b",
        "table": r"(?i)\b(?:table|tab)\.?\s*\d+(?:[-.:]?\d+)?\b",
        "numeric_point_section": r"^\s*(\d+)\.\s([A-Z][\w:]+[ \w+]+)(<--.*-->)*\n",
        "rome_point_section": r"^\s*([IVX]+)\.\s([A-Z][\w:]+[ \w+]+)(<--.*-->)*\n",
        "numeric_section": r"^s*(\d+)\s([A-Z][\w:]+[ \w+]+)(<--.*-->)*\n",
        "generic_section_title": r"^(\d+|[IVX]+)[\.]?\s([A-Z][\w:]+[ \w+]+)(<--.*-->)*\n",
        "table_description": r"(TABLE|Table|table)\s*\d+\.[\s\S]+?\n",
        #"generic_section": r"^\s*([A-Z][a-zA-Z\s]+)$",
        "citation1": r"^\[(\d)\]\s*([^\[]+)\n",
        "bold_tag": r"<--bold-->",
        "italic_tag": r"<--italic-->",
        "size_tag": r"<--size=(\d+(\.\d+)?)-->",
        "page_start_tag": r"<--page_start:(\d+)-->",
        "page_end_tag": r"<--page_end:(\d+)-->",
        "image_tag": r"<--image width=(\d+(\.\d+)?) height=(\d+(\.\d+)?)-->",
    }
    
    common_section_titles = [
        "introduction", "background", "related work", 
        "methodology", "method", "methods", "experiments",
        "results", "discussion", "evaluation", "conclusion", "references",
        "future work", "research questions", "threats to validity"
    ]

    section_position_map = {
        "introduction": {"page": [1,2], "percentage": 0.08},
        "background": {"page": [2,3], "percentage": 0.15},
        "related work": {"page": 4, "percentage": 0.20},
        "methodology": {"page": 5, "percentage": 0.35},
        "method": {"page": 5, "percentage": 0.35},
        "methods": {"page": 5, "percentage": 0.35},
        "experiments": {"page": 7, "percentage": 0.55},
        "experimental setup": {"page": 7, "percentage": 0.55},
        "results": {"page": 8, "percentage": 0.70},
        "discussion": {"page": 9, "percentage": 0.75},
        "evaluation": {"page": 8, "percentage": 0.70},
        "conclusion": {"page": 10, "percentage": 0.85},
        "references": {"page": 11, "percentage": 0.95},
        "future work": {"page": 10, "percentage": 0.85},
        "acknowledgments": {"page": 10, "percentage": 0.90},
        "appendix": {"page": 12, "percentage": 0.98}
    }

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
                text += f"<--page_start:{idx+1}-->"
                text +=  page.get_text()
                text += f"<--page_end:{idx+1}-->"
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
            
            all_line_sizes = []

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
                            all_line_sizes.append(most_common_size)
                            

                        if line_is_bold:
                            tags.append("<--bold-->")

                        text += line_text + "".join(tags) + "\n"

                    text += "\n"
                text += f"<--page_end:{page_num+1}-->\n\n"
            
            # Calculate the mode of all line sizes in the document
            doc_most_common_size = mode(all_line_sizes) if all_line_sizes else None

            return text, page_num+1, doc_most_common_size

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
    def default_pdf_cleaning(text: str) -> str:
        """Clean the PDF text by removing unwanted characters and patterns.

        Args:
            text (str): The text to clean.

        Returns:
            str: The cleaned text.
        """
        text = re.sub(PDFHandler.regex_patterns["non_ascii"], "", text)
        text = re.sub(PDFHandler.regex_patterns["unicode_spaces"], " ", text)
        text = re.sub(PDFHandler.regex_patterns["figure"], "", text)
        text = re.sub(PDFHandler.regex_patterns["table"], "", text)
        return text

    @staticmethod
    def tiebreaker_policy(sections:  List[SectionInfo], last_find_position: int) -> SectionInfo:
        """This function recieves a list of sectionsinfo that are competting for the same position
        and returns the best section based on the confidence score and the last find position.

        Args:
            sections (List[SectionInfo]): _description_
            last_find_position (int): _description_

        Returns:
            SectionInfo: _description_
        """
        if not sections:
            logging.warning("No sections provided for tiebreaker.")
            return None

        max_confidence = max(section.confidence_score for section in sections)

        tied_sections = [section for section in sections if section.confidence_score == max_confidence]

        if len(tied_sections) == 1:
            best_section =  tied_sections[0]
        
        elif last_find_position == -1:
            best_section = min(tied_sections, key=lambda x: x.position) if tied_sections else sections[0]

        else:
            best_section = max(tied_sections, key=lambda x: abs(x.position - last_find_position)) if tied_sections else sections[0]
        
        return best_section

    @staticmethod
    def voting_policy(sections: List[SectionInfo]) -> List[SectionInfo]:
        
        sorted_sections = sorted(sections, key=lambda x: (getattr(x, 'section_number', 0), getattr(x, 'position', 0)))
        
        for section in sorted_sections:

            section.update_metrics("is_bold", True if re.search(PDFHandler.regex_patterns["bold_tag"], section.section_title) else False)
            # size_match = re.search(PDFHandler.regex_patterns["size_tag"], section.section_title)
            # if size_match:
            #     font_size = float(size_match.group(1))
            #     section.update_metrics("font_size_larger", font_size > 1.0)
            section.update_metrics("has_common_title", True if any(title.lower() in section.section_title.lower() for title in PDFHandler.common_section_titles) else False)
            section.update_metrics("has_no_ponctuation", False if re.search(PDFHandler.regex_patterns["ponctuation_ASCII"], section.section_title) else True)

            section.calculate_confidence_score()

        best_sections = []
        last_find_position = -1

        #TODO : rethinking the structure of this rule executioning
        for section in sorted_sections:
            if best_sections and section.section_number == best_sections[-1].section_number:
                tied_sections = [section, best_sections[-1]]
                best_section = PDFHandler.tiebreaker_policy(tied_sections, last_find_position)
                best_sections[-1] = best_section
            else:
                best_section = section
                best_sections.append(best_section)

            last_find_position = section.position
        
        
        return best_sections
        
    @staticmethod
    def extract_section_from_text(text: str, section_pattern: str) -> List[SectionInfo]:
        sections = []
        matches = re.finditer(section_pattern, text, re.MULTILINE)
        introduction_matches = re.finditer(PDFHandler.regex_patterns["introduction"], text)

        # if introduction_matches:
        #     introduction_posiition = introduction_matches[0].start()

        if not matches:
            logging.info("No matches found for the given pattern.")
            return sections
        
        page_start_matches = re.finditer(PDFHandler.regex_patterns["page_start_tag"], text, re.MULTILINE)
        page_end_matches = re.finditer(PDFHandler.regex_patterns["page_end_tag"], text, re.MULTILINE)

        page_start_positions = [match.start() for match in page_start_matches]
        page_end_positions = [match.start() for match in page_end_matches]
        
        for match in matches:
            section_number = match.group(1)
            section_title = match.group(2)
            position = match.start()

            page_number = next(
                (i + 1 for i, (start, end) in enumerate(zip(page_start_positions, page_end_positions))
                 if start <= position < end),
                -1
            )
            
            section_info = SectionInfo(section_number, section_title, page_number, position)
            sections.append(section_info)
        
        return sections

    @staticmethod
    def get_sections_text(text: str, sections: list[SectionInfo]) -> str:
        for indx, section in enumerate(sections):
            if indx == len(sections) - 1:
                section.content = text[section.position:]
            else:
                section.content = text[section.position:sections[indx + 1].position]

    @staticmethod
    def extract_all_pdf_sections(doc: fitz.Document, pattern: str) -> List[SectionInfo]:
        """Extract all sections from a PDF document using regex patterns.

        Args:
            doc (fitz.Document): The PDF document object.

        Returns:
            List[SectionInfo]: A list of SectionInfo objects containing section details.
        """
        PDFHandler.try_open(doc)
        text, page_count = PDFHandler.simple_extraction(doc)
        section_titles = PDFHandler.find_pdf_topics_outline(doc)
        print(section_titles)

        text = PDFHandler.default_pdf_cleaning(text)

        sections = PDFHandler.extract_section_from_text(text, PDFHandler.regex_patterns[pattern])
        # for section in sections: 
        #     print(section.section_title + " " + str(section.section_number))

        final_sections = PDFHandler.voting_policy(sections)

        PDFHandler.get_sections_text(text, final_sections)
        
        return final_sections
    
    @staticmethod
    def find_pattern_in_text(text: str, pattern: str, debug: bool = False) -> SectionInfo:
        """Find all occurrences of a pattern in the text.

        Args:
            text (str): The text to search.
            pattern (str): The regex pattern to match.

        Returns:
            List[Tuple[int, str]]: A list of tuples containing the position and matched text.
        """
        matches = list(re.finditer(pattern, text, re.MULTILINE))
        if debug:
            print(f"Found {len(matches)} matches:")
        
        generate_page_start_end_list = PDFHandler.generate_page_start_end_list(text)
        section_array = []
        for match in matches:
            page_number = -1
            for idx, ((start_pos, _), (end_pos, _)) in enumerate(generate_page_start_end_list):
                if start_pos <= match.start() < end_pos:
                    page_number = idx + 1  
                    break
            matched_text = match.group(0)
            section_number = match.group(1)
            section_title = match.group(2)
            bold = True if re.search(PDFHandler.regex_patterns["bold_tag"], matched_text) else False
            size_match = re.search(PDFHandler.regex_patterns["size_tag"], matched_text)
            section_info = SectionInfo(
                section_number=section_number,
                section_title=section_title,
                page_number=page_number,
                position=match.start(),
                bold=bold,
                size=float(size_match.group(1)) if size_match else 0.0,
            )
            section_array.append(section_info)

        return section_array
    
    @staticmethod
    def generate_page_start_end_list(text: str) -> List[Tuple[int, int]]:
        """Generate a list of tuples containing the start and end positions of each page in the text.

        Args:
            text (str): The text to search.

        Returns:
            List[Tuple[int, int]]: A list of tuples containing the start and end positions of each page.
        """
        page_start_list = [(match.start(), match.group(0)) for match in re.finditer(PDFHandler.regex_patterns["page_start_tag"], text)]
        page_end_list = [(match.start(), match.group(0)) for match in re.finditer(PDFHandler.regex_patterns["page_end_tag"], text)]
        return list(zip(page_start_list, page_end_list))
    
    @staticmethod
    def insert_section_into_sqlite(db_connection, sections: SectionInfo, id_pdf: int):
        """Insert a section into the SQLite database.

        Args:
            db_connection: The SQLite database connection.
            section (SectionInfo): The section to insert.
        """
        cursor = db_connection.cursor()
        for section in sections:
            cursor.execute(
                "INSERT INTO extracted_text (section_number, pdf_id, section_title, page_number, position, content) VALUES (?, ?, ?, ?, ?, ?)",
                (section.section_number, id_pdf, section.section_title, section.page_number, section.position, section.content)
            )
        db_connection.commit()

    @staticmethod
    def create_tables(db_connection):
        """Create the sections table in the SQLite database if it does not exist."""
        cursor = db_connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pdfs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pdf_name TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS extracted_text (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pdf_id INTEGER NOT NULL,
                section_number TEXT NOT NULL,
                section_title TEXT NOT NULL,
                page_number INTEGER NOT NULL,
                position INTEGER NOT NULL,
                content TEXT,
                FOREIGN KEY (pdf_id) REFERENCES pdfs(id)
            )
        """)
        db_connection.commit()

if __name__ == "__main__":
    path = "/home/PUC/Documentos/AutoSLR/papers_pdf/Scopus/Krishna2021.pdf"
    db_connection = sqlite3.connect("simple_regex.db")
    
    doc = PDFHandler.try_open(path)
    if doc is None:
        print("Error opening the PDF")
        exit(1)
    
    text, page_count, doc_most_common_size = PDFHandler.tagged_text_extraction(doc)
    with open("./output.txt", "w") as f:
        f.write(text)

    # PDFHandler.create_tables(db_connection)
    # text, page_count = PDFHandler.simple_extraction(doc)
    # text = PDFHandler.default_pdf_cleaning(text)
    # sections = PDFHandler.find_pattern_in_text(text, PDFHandler.regex_patterns["generic_section_title"])
    # for section in sections:
    #     print(f"Section: {section.section_title}, Page: {section.page_number}, Position: {section.position}")
    # PDFHandler.insert_section_into_sqlite(db_connection, sections)
