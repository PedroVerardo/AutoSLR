import logging
import datetime
import os
import time

import numpy as np

from .pdf_handler import PDFHandler
from ..models import ServiceType
from ..config import KafkaConfig
from ..database import insert_article, insert_segment, insert_chunk, batch_insert_segments, batch_insert_chunks
from ..database import get_db
from ..models import Article, Segment, Chunk
from ..utils.chunking import ChunkText
from ..database.session import Base, engine

#TODO: make the request more reliable, make it possible to change the section pattern based on the tag type
def process_extraction_message(message, model, data_path, db):
    """
    Process the Kafka message, extract titles from the PDF, and return them.

    Args:
        message (dict): The Kafka message containing the PDF path.

    Returns:
        list[str]: A list of titles extracted from the PDF.
    """
    archive_name = message.get("archive_name")
    section_pattern = message.get("section_pattern")

    pdf_path = None

    for root, dirs, files in os.walk(data_path):
        for file in files:
            if archive_name in file and file.lower().endswith('.pdf'):
                pdf_path = os.path.join(root, file)
                logging.info(f"Found matching PDF: {pdf_path}")
                break
    
    if pdf_path is None:
        logging.error(f"PDF file not found for title: {archive_name}")
        return []

    doc = PDFHandler.try_open(pdf_path)

    if not doc:
        print(f"Failed to open PDF: {pdf_path}")
        return []
    
    tag = "bold"
    
    text, page_count = PDFHandler.tagged_extraction(doc, tag)
    if not text:
        logging.error(f"Failed to extract text from PDF: {pdf_path}")
        return []

    extracted_text = PDFHandler.extract_text_with_regex(text, PDFHandler.regex_patterns[section_pattern])

    if not extracted_text:
        logging.error(f"No text extracted using regex pattern: {section_pattern}")
        return []

    titles = [value for value in extracted_text]
    qtd = len(titles)
    doc.close()

    ####### Insert into DB #######

    segment_buff = np.empty(qtd, dtype=Segment)

    Article_obj = Article(
        title=archive_name,
        upload_date=datetime.date.fromtimestamp(time.time()),
    )

    err, info = insert_article(db, Article_obj, auto_commit=False)
    
    if err:
        logging.error(f"Error inserting article: {info}")
        return []
    
    for idx, value in enumerate(extracted_text.values()):
        segment_obj = Segment(
            article_id=Article_obj.id,
            segment_title=value['title'],
            segment_title_vector=model.encode(value['title'], show_progress_bar=False),
            segment_text=value['text'],
        )

        segment_buff[idx] = segment_obj

        chunk_list = ChunkText.fixed_window_splitter(value['text'], 384)
        qtd = len(chunk_list)
        chunk_buff = np.empty(qtd, dtype=Chunk)
        err, seg_info = insert_segment(db, segment_obj, auto_commit=False)
        if err:
            logging.error(f"Error inserting segment: {seg_info}")
            return []
        logging.info(f"Segment_id: {seg_info}")
        for chunk_idx, chunk in enumerate(chunk_list):
            logging.info(f"Chunk: {chunk_idx} of {qtd}")
            chunk_obj = Chunk(
                segment_id=seg_info,
                chunk_text=chunk,
                chunk_vector=model.encode(chunk, show_progress_bar=False),
            )
            chunk_buff[chunk_idx] = chunk_obj
            err, chunk_info = insert_chunk(db, chunk_obj, auto_commit=False)
            if err:
                logging.error(f"Error inserting chunk: {chunk_info}")
                return []
        
        db.commit()

        # Insert segments and chunks only if buffers are not empty
        # if len(segment_buff) > 0:
        #     err, info = batch_insert_segments(db, segment_buff, auto_commit=True)
        #     if err:
        #         logging.error(f"Error inserting segments: {info}")
        #         return []

        # if len(chunk_buff) > 0:
        #     err, info = batch_insert_chunks(db, chunk_buff, auto_commit=True)
        #     if err:
        #         logging.error(f"Error inserting chunks: {info}")
        #         return []

    return titles