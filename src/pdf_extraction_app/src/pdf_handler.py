from collections import OrderedDict
import re

import fitz

from ..utils.regex_pattern import RegexPattern

class PDFHandler:
    def __init__(self):
        self.doc = None

    def simple_extraction(pdf_path: str) -> tuple[str, int]:
        """This function extracts text from a PDF file and returns the text along with the number of pages.

        Args:
            pdf_path (str): The path to a PDF file

        Returns:
            tuple[str, int]: The text inside the pdf(without any cleaning)
        """
        try:
            doc = fitz.open(pdf_path)
            text = ''
            cont = 0
            for page in doc:
                text += page.get_text()
                cont += 1
            doc.close()
            return (text, cont)
        
        except FileNotFoundError:
            print(f"File not found: {pdf_path}")

        except Exception as e:
            print(f"An error occurred: {e} in {__file__} ")

    def tagged_extraction(pdf_path: str, span_tag: str) -> str:
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
            doc = fitz.open(pdf_path)
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

            doc.close()
            return text, page_cont
        except FileNotFoundError:
            print(f"File not found: {pdf_path}")
            return None
        except Exception as e:
            print(f"An error occurred: {e} in {__file__} ")
            return None
        

    def get_metadata(self):
        """This function extracts metadata from a PDF file.

        Args:
            pdf_path (str): The path to a PDF file.

        Returns:
            dict: A dictionary containing the metadata of the PDF file.
        """
        try:
            doc = fitz.open(self.pdf_path)
            metadata = doc.metadata
            doc.close()
            return metadata
        except FileNotFoundError:
            print(f"File not found: {self.pdf_path}")
            return None
        except Exception as e:
            print(f"An error occurred: {e} in {__file__} ")
            return None

# Example usage
if __name__ == "__main__":
    pdf_handler = PDFHandler("example.pdf")
    text = pdf_handler.extract_text()
    print("Extracted Text:", text)

    metadata = pdf_handler.get_metadata()
    print("Metadata:", metadata)