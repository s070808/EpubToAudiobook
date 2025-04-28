# ============================================
# EPUB to Audiobook Converter (Full Script)
# ============================================

import os
import re
import asyncio
import edge_tts
from ebooklib import epub
from bs4 import BeautifulSoup

# --------------------------------------------
# Constants
# --------------------------------------------

ITEM_DOCUMENT = 9                     # EbookLib document type constant
SECTION_HEADER_MARKER = '#####START_HEADING#####'
CHUNK_MARKER = '#####CHUNK#####'
MAX_CHUNK_SIZE = 4000                  # Edge TTS API chunk size limit

CHAPTER_KEY = '_chapter_'              # Prefix for chapter filenames
FILENAME = "Nick_Carter_-_[Killmaster_027]_-_Assignment_Israel"

# Paths (initialized later in preamble())
EPUB_PATH = ''
CHAPTERS_PATH = ''
MP3_PATH = ''


# --------------------------------------------
# EPUB Processing Functions
# --------------------------------------------

def emphasize_headings(soup):
    """Replace all heading tags (h1-h6) with special marker lines."""
    for level in range(1, 7):
        for tag in soup.find_all(f'h{level}'):
            heading_text = tag.get_text(strip=True)
            new_string = f"{SECTION_HEADER_MARKER}{heading_text}\n"
            tag.replace_with(new_string)


def extract_paragraphs_from_epub():
    """Extract cleaned paragraphs from the EPUB file."""
    book = epub.read_epub(EPUB_PATH)
    paragraphs = []

    for item in book.get_items():
        if item.get_type() == ITEM_DOCUMENT:
            soup = BeautifulSoup(item.get_content(), 'html.parser')

            # Remove unwanted HTML elements
            for tag in soup.find_all(['script', 'style', 'head', 'title', 'meta', '[document]']):
                tag.decompose()

            # Mark all headings with a special marker
            emphasize_headings(soup)

            # Collect visible cleaned text
            for text in soup.stripped_strings:
                clean_text = ' '.join(text.split())
                if clean_text:
                    paragraphs.append(clean_text)

    return paragraphs


# --------------------------------------------
# Paragraph and Chapter Utilities
# --------------------------------------------

def split_paragraphs_by_heading_marker(paragraphs):
    """Split paragraphs into chapters based on heading markers."""
    chapters = []
    current_chapter = []

    for para in paragraphs:
        if para.startswith(SECTION_HEADER_MARKER):
            if current_chapter:
                chapters.append(current_chapter)
            current_chapter = [para]
        else:
            current_chapter.append(para)

    if current_chapter:
        chapters.append(current_chapter)

    return chapters


def split_paragraphs_into_chunks(paragraphs):
    """Split paragraphs into manageable text chunks (max size)."""
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        if len(current_chunk) + len(para) + 2 < MAX_CHUNK_SIZE:
            current_chunk += para + "\n\n"
        else:
            chunks.append(current_chunk.rstrip("\n\n"))
            current_chunk = para + "\n\n"

    if current_chunk:
        chunks.append(current_chunk.rstrip("\n\n"))

    return chunks


def save_chapters_to_file(chapters):
    """Save each chapter into its own text file with padded numbering."""
    for i, chap in enumerate(chapters):
        path = os.path.join(CHAPTERS_PATH, f'{CHAPTER_KEY}{i:04d}.txt')
        with open(path, 'w', encoding='utf-8') as f:
            for para in chap:
                cleaned_para = para.replace(SECTION_HEADER_MARKER, '').strip()
                if cleaned_para:
                    f.write(cleaned_para)
                    f.write("\n\n")  # Double newline for paragraph separation


def load_chapter_files(chapters_path):
    """Find and return all chapter text files sorted by number."""
    chapter_files = []
    for filename in sorted(os.listdir(chapters_path)):
        if re.match(r'_chapter_\d+\.txt$', filename):
            chapter_files.append(os.path.join(chapters_path, filename))
    return chapter_files


def load_paragraphs_from_file(file_path):
    """Load paragraphs from a saved chapter text file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    paragraphs = [para.strip() for para in content.split("\n\n") if para.strip()]
    return paragraphs


# --------------------------------------------
# TTS (Text-to-Speech) Functions
# --------------------------------------------

async def text_to_mp3(text_chunks, output_path, voice="en-US-AriaNeural"):
    """Convert a list of text chunks to a single MP3 file using edge_tts."""
    with open(output_path, 'wb') as out_f:
        total_chunks = len(text_chunks)

        for idx, chunk in enumerate(text_chunks, 1):
            print(f"\n=== Processing chunk {idx}/{total_chunks} ===")
            print(chunk)
            print("\n=== End of chunk ===\n")

            communicate = edge_tts.Communicate(text=chunk, voice=voice)
            async for chunk_data in communicate.stream():
                if chunk_data["type"] == "audio":
                    out_f.write(chunk_data["data"])


async def process_all_chapters_to_mp3():
    """Convert each chapter text file into an MP3 file."""
    chapter_files = load_chapter_files(CHAPTERS_PATH)

    for chapter_file in chapter_files:
        print(f"Processing {chapter_file}...")

        paragraphs = load_paragraphs_from_file(chapter_file)
        chunks = split_paragraphs_into_chunks(paragraphs)

        chapter_num = int(os.path.splitext(os.path.basename(chapter_file))[0].split("_")[-1])
        output_mp3_path = os.path.join(MP3_PATH, f"chapter_{chapter_num:04d}.mp3")

        os.makedirs(MP3_PATH, exist_ok=True)

        await text_to_mp3(chunks, output_mp3_path, voice="en-US-AriaNeural")


# --------------------------------------------
# Workflow Functions
# --------------------------------------------

def extract_epub_to_clean_text():
    """Main flow: extract paragraphs from EPUB and save as chapter files."""
    paragraphs = [SECTION_HEADER_MARKER] + extract_paragraphs_from_epub()

    chapters = split_paragraphs_by_heading_marker(paragraphs)
    save_chapters_to_file(chapters)


def preamble():
    """Prepare paths and output folders."""
    global EPUB_PATH, CHAPTERS_PATH, MP3_PATH

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    base_dir_epub = os.path.join(BASE_DIR, "epub")
    base_dir_txt = os.path.join(BASE_DIR, "txt", FILENAME)
    base_dir_mp3 = os.path.join(BASE_DIR, "mp3", FILENAME)

    os.makedirs(base_dir_txt, exist_ok=True)
    os.makedirs(base_dir_mp3, exist_ok=True)

    EPUB_PATH = os.path.join(base_dir_epub, FILENAME + ".epub")
    CHAPTERS_PATH = base_dir_txt
    MP3_PATH = base_dir_mp3


# --------------------------------------------
# Main Execution
# --------------------------------------------

if __name__ == "__main__":
    preamble()
    extract_epub_to_clean_text()
    asyncio.run(process_all_chapters_to_mp3())
