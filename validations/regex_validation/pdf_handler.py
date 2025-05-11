import re

import fitz
from statistics import mode

# Removed unused import of RegexPattern

class PDFHandler:
    regex_patterns = {
        "non_ascii": "[\\x00-\\x08\\x0B-\\x1F\\x7F-\\x9F\\xA0]",
        "unicode_spaces": "[\\u00A0\\u2000-\\u200F\\u2028\\u2029\\u202F\\u3000]",
        "introduction": "\\n*\\s*[Ii][Nn][Tt][Rr][Oo][Dd][Uu][Cc][Tt][Ii][Oo][Nn]\\s*\\n*",
        "references": "\\n\\s*[Rr][Ee][Ff][Ee][Rr][Ee][Nn][Cc][Ee][Ss]\\s*\\n",
        "numeric_point_section": r"<--bold--><--size:[\d.]+-->\s*(\d)\.\s+([A-Z][^<]+)<--size:[\d.]+--><--bold-->",
        "rome_point_section": r"(?:<--bold-->)?<--size:[\d.]+-->\s*([IVX]+)\.\s+([A-Z][^<]+)<--size:[\d.]+-->(?:<--bold-->)?",
        "numeric_section": r"(?:<--bold-->)?<--size:[\d.]+-->\s*(\d)\s+([A-Z][^<]+)<--size:[\d.]+-->(?:<--bold-->)?",
        "table_description": "(TABLE|Table|table)\\s*\\d+\\.[\\s\\S]+?",
        "citation1": "\\[(\\d)\\]\\s*([^\\[]+)"
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
    def simple_extraction(doc: fitz.Document ) -> tuple[str, int]:
        """This function extracts text from a PDF file and returns the text along with the number of pages.

        Args:
            pdf_path (str): The path to a PDF file

        Returns:
            tuple[str, int]: The text inside the pdf(without any cleaning)
        """
        try:
            text = ''
            cont = 0
            for page in doc:
                text += page.get_text()
                cont += 1

            return (text, cont)

        except Exception as e:
            print(f"An error occurred: {e} in {__file__} ")

    @staticmethod
    def tagged_extraction(doc: fitz.Document, span_tag: str) -> tuple[str, int, float]:
        """This function allows the reader to identify points of interest inside the text.
        
        Args:
            doc (fitz.Document): The PDF document object.
            span_tag (str): A tag like "bold", "italic", etc., to mark the line that has a word in italic.
        
        Returns:
            tuple[str, int, float]: The text inside the PDF (without any cleaning) with tags like "bold", "italic", etc.,
            the number of pages, and the mode of font sizes.
        """
        try:
            page_cont = range(len(doc))
            text = ''
            font_sizes = []
            previous_line_buffer = ""
            
            # Define patterns for "bold-like" fonts
            bold_patterns = [
                "bold", "heavy", "black", "semibold", "demi", "medium",
                "thick", "wide", "expanded"
            ]
            
            # Define cleaning pattern for various Unicode spaces and invisible characters
            clean_pattern = re.compile(r'[\x00-\x08\x0B-\x1F\x7F-\x9F\xA0\u00A0\u2000-\u200F\u2028\u2029\u202F\u3000\uFEFF]+')
            
            for page_num in page_cont:
                page = doc[page_num]
                text_blocks = page.get_text("dict")["blocks"]
                
                for block in text_blocks:
                    if "lines" not in block:
                        continue
                    
                    for i, line in enumerate(block["lines"]):
                        size_tag = ""
                        searched_tag = ""
                        
                        if line["spans"]:
                            font_size = line["spans"][0].get("size", "")
                            font_sizes.append(font_size)
                            
                        # Enhanced tag detection
                        find_tag = False
                        if span_tag.lower() == "bold":
                            # Check for any bold-like pattern in font name
                            find_tag = any(
                                any(pattern in span["font"].lower() for pattern in bold_patterns)
                                for span in line["spans"]
                            )
                        else:
                            # Original logic for other tags
                            find_tag = any(span_tag.lower() in span["font"].lower() for span in line["spans"])
                        
                        # You could also check font weight if available
                        # Some PDFs include weight information
                        for span in line["spans"]:
                            # Check if font weight indicates bold
                            weight = span.get("font-weight", 0)
                            if weight >= 600:  # CSS font-weight: 600+ is considered bold
                                find_tag = True
                                break
                        
                        # Join span texts and clean them
                        line_text = " ".join(span["text"] for span in line["spans"]).strip()
                        # Clean Unicode spaces and replace with regular space
                        line_text = clean_pattern.sub(' ', line_text)
                        # Normalize multiple spaces to single space
                        line_text = re.sub(r'\s+', ' ', line_text).strip()
                        
                        if find_tag:
                            searched_tag += "<--" + span_tag + "-->"
                        if font_size:
                            size_tag = f"<--size:{font_size}-->"
                        
                        # Check if we have a buffered previous line
                        if previous_line_buffer:
                            # Combine with current line with a single space
                            cleaned_buffer = clean_pattern.sub(' ', previous_line_buffer)
                            combined_text = cleaned_buffer + " " + line_text
                            # Normalize spaces again after combination
                            combined_text = re.sub(r'\s+', ' ', combined_text)
                            
                            text += combined_text
                            text += size_tag
                            text += searched_tag
                            text += "\n"
                            previous_line_buffer = ""
                        else:
                            # Check if current line should be buffered
                            if len(line_text.strip()) == 1 and i < len(block["lines"]) - 1:
                                # Buffer this line to combine with next
                                previous_line_buffer = searched_tag + size_tag + line_text
                            else:
                                # Normal line processing
                                text += searched_tag
                                text += size_tag
                                text += line_text
                                text += size_tag
                                text += searched_tag
                                text += "\n"
            
            # Handle any remaining buffered line
            if previous_line_buffer:
                text += previous_line_buffer + "\n"
            
            font_mode = mode(font_sizes) if font_sizes else None
            return text, len(page_cont), font_mode
        
        except Exception as e:
            print(f"An error occurred: {e} in {__file__} ")
            return None, None, None
        
    @staticmethod
    def get_metadata(doc: fitz.Document):
        """This function extracts metadata from a PDF file.

        Args:
            pdf_path (str): The path to a PDF file.

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
    def extract_text_with_regex(text: str, regex_pattern: str, mode: float) -> dict[str, dict[str, str]]:
        try:
            results = {}
            matches = list(re.finditer(regex_pattern, text, re.MULTILINE))
            for match in matches:
                # Extract the font size from the match
                full_match = match.group(0)
                # print(full_match)
                size_match = re.search(r'<--size:([\d.]+)-->', full_match)
                if size_match:
                    font_size = float(size_match.group(1))
                    # print(f"Font Size: {font_size} {mode}")
                    
                    # Only process if font size is bigger than mode
                    if font_size >= mode:
                        match_number = match.group(1)
                        match_title = match.group(2).strip()
                        # print(f"Match Number: {match_number}, Match Title: {match_title}")
                        
                        start = match.start()
                        # Find the end of this section (start of next section or end of text)
                        end = matches[matches.index(match) + 1].start() if matches.index(match) + 1 < len(matches) else len(text)
                        extracted_text = text[start:end]
                        
                        # Clean the extracted text by removing all tags
                        clean_text = re.sub(r'<--[^>]+-->', '', extracted_text)
                        clean_text = clean_text.strip()
                        
                        if match_number not in results:
                            results[match_number] = {
                                "title": "",
                                "text": ""
                            }
                        
                        results[match_number]["title"] = match_title
                        results[match_number]["text"] = clean_text
            
            return results
        
        except Exception as e:
            print(f"An error occurred: {e} in {__file__} ")
            return None

if __name__ == "__main__":
    # simple usage for futher reference
    path = "/home/pedro/Documents/Rag_test/grpc/papers_pdf/ACM/isaev2023_hpcc.pdf"
    
    doc = PDFHandler.try_open(path)

    # <--bold--><--size:11.0-->7 Discussion<--size:11.0--><--bold-->
    # smode is mode of statistics
    taged_text, _, smode = PDFHandler.tagged_extraction(doc, "bold")
    print("Extracted Text:", taged_text)
    print("mode: ", smode)

    metadata = PDFHandler.get_metadata(doc)
    #print("Metadata:", metadata)

    regex_pattern = PDFHandler.regex_patterns["numeric_section"]

    extracted_text = PDFHandler.extract_text_with_regex(taged_text, regex_pattern, smode)


    #printing the title of each extracted text
    for key, value in extracted_text.items():
        print(f"Title: {key} {value['title']}")

    # matches = re.findall(regex_pattern, text)
    # print(matches)


    # doc.close()