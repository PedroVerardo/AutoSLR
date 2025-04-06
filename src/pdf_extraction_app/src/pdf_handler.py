import re

import fitz

# Removed unused import of RegexPattern

class PDFHandler:

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
    def tagged_extraction(doc: fitz.Document, span_tag: str) -> str:
        """This functino possibility the next reader to identify point of interest inside the text.

        Args:
            pdf_path (str): The path to a PDF file.
            span_tag (str): A tag like "bold", "italic", etc. To mark the line that have a word in italic.

        Returns:
            tuple[str, int]: The text inside the pdf(without any cleaning) with tags like "bold", "italic", etc.
            Example:
                "1 Introduction. <--bold-->\n"
        """
        try:
            page_cont = range(len(doc))
            text = ''
            for page_num in page_cont:
                page = doc[page_num]
                text_blocks = page.get_text("dict")["blocks"]

                for block in text_blocks:
                    if "lines" not in block:
                        continue

                    for line in block["lines"]:
                        find_tag = any(span_tag in span["font"].lower() for span in line["spans"])
                        line_text = " ".join(span["text"] for span in line["spans"]).strip()
                        text += line_text
                        if find_tag:
                            text += "<--"+ span_tag +"-->"
                        text += "\n"

            return text, page_cont
        
        except Exception as e:
            print(f"An error occurred: {e} in {__file__} ")
            return None
        
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
    def extract_text_with_regex(text: str, regex_pattern: str) -> list[str]:
        try:
            results = {}
            matches = list(re.finditer(regex_pattern, text, re.MULTILINE))
            for match in matches:
                matched_text = match.group()
                match_number = match.group(1)
                start = match.start()
                end = matches[matches.index(match) + 1].start() if matches.index(match) + 1 < len(matches) else len(text)
                extracted_text = text[start:end]
                if matched_text not in results:
                    results[match_number] = {
                        "title": "",
                        "text": ""
                    }
                results[match_number]["title"] = matched_text[1:-11]
                results[match_number]["text"] = extracted_text
            return results
        
        except Exception as e:
            print(f"An error occurred: {e} in {__file__} ")
            return None

if __name__ == "__main__":
    # simple usage for futher reference
    path = "/home/pedro/Documents/Rag_test/grpc/papers_pdf/ScienceDirect/Arcaini2020.pdf"
    
    doc = PDFHandler.try_open(path)

    text, _ = PDFHandler.tagged_extraction(doc, "bold")
    # print("Extracted Text:", text)

    metadata = PDFHandler.get_metadata(doc)
    # print("Metadata:", metadata)

    regex_pattern = r"\n(\d)\.\s+(?!\d)[\w\s]+<--bold-->\n"

    extracted_text = PDFHandler.extract_text_with_regex(text, regex_pattern)

    # printing the title of each extracted text
    for key, value in extracted_text.items():
        print(f"Title: {value['title']}")

    # matches = re.findall(regex_pattern, text)
    # print(matches)


    doc.close()