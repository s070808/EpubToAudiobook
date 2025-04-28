import os
import asyncio
import edge_tts
from ebooklib import epub
from bs4 import BeautifulSoup
import math

ITEM_DOCUMENT = 9
SECTION_HEADER_MARKER = '#####START_HEADING#####'
CHUNK_MARKER = '#####CHUNK#####'
MAX_CHUNK_SIZE = 4000

FILENAME = "Nick_Carter_-_[Killmaster_027]_-_Assignment_Israel"
EPUB_PATH = ''
PARAGRAPHS_PATH = ''
CHAPTERS_PATH = ''
CHUNKS_PATH = ''
MP3_PATH = ''

CHAPTER_KEY = '_chapter_'

def emphasize_headings(soup):
    for level in range(1, 7):  # for h1 to h6
        for tag in soup.find_all(f'h{level}'):
            heading_text = tag.get_text(strip=True)
            new_string = f"{SECTION_HEADER_MARKER}{heading_text}\n"
            tag.replace_with(new_string)

def extract_paragraphs_from_epub():
    book = epub.read_epub(EPUB_PATH)
    paragraphs = []

    for item in book.get_items():
        if item.get_type() == ITEM_DOCUMENT:  # ITEM_DOCUMENT
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            
            # Remove unwanted elements (style, script, head, etc.)
            for tag in soup.find_all(['script', 'style', 'head', 'title', 'meta', '[document]']):
                tag.decompose()

            # Then inject heading markers
            emphasize_headings(soup)

            # Now grab all visible text
            texts = soup.stripped_strings  # Generator: yields clean text nodes

            for text in texts:
                clean_text = ' '.join(text.split())
                if clean_text:
                    paragraphs.append(clean_text)

    return paragraphs



async def text_to_mp3(text_chunks, output_path, voice="en-US-AriaNeural"):
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
            break# - use to debug rendering, only creates a single chunk


def load_chunks_from_file(output_path):
    with open(output_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split based on the exact separator
    chunks = content.split(CHUNK_MARKER)

    # Only remove empty chunks caused by extra separators, but DO NOT strip user content
    chunks = [chunk for chunk in chunks if chunk != '']

    return chunks


def create_audiobook(chunks_path, output_mp3_path, voice="en-US-AriaNeural"):
    chunks = load_chunks_from_file(chunks_path)
    asyncio.run(text_to_mp3(chunks, output_mp3_path, voice))

def save_chunks_to_file(chunks):
    with open(CHUNKS_PATH, 'w', encoding='utf-8') as f:
        for chunk in chunks:
            f.write(chunk)
            f.write(CHUNK_MARKER)  # separator between chunks

def split_paragraphs_into_chunks(paragraphs):
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        if len(current_chunk) + len(para) + 1 < MAX_CHUNK_SIZE:
            current_chunk += para + "\n\n"
        else:
            chunks.append(current_chunk.rstrip("\n\n"))  # only strip the added newline
            current_chunk = para + "\n\n"

    if current_chunk:
        chunks.append(current_chunk.rstrip("\n"))

    return chunks

def save_paragraphs_to_file(paragraphs):
    with open(PARAGRAPHS_PATH, 'w', encoding='utf-8') as f:
        for para in paragraphs:
            f.write(para)
            f.write("\n\n")  # double newlines between paragraphs (for clarity)

def save_chapters_to_file(chapters):
    for i, chap in enumerate(chapters):
        path = os.path.join(CHAPTERS_PATH, f'{CHAPTER_KEY}{i}.txt')#CHAPTERS_PATH + f'{CHAPTER_KEY}{i}.txt'
        with open(path, 'w', encoding='utf-8') as f:
            for para in chap:
                cleaned_para = para.replace(SECTION_HEADER_MARKER, '').strip()
                if cleaned_para:  # only write non-empty paragraphs
                    f.write(cleaned_para)
                    f.write("\n\n")  # double newlines between paragraphs (for clarity)



def split_paragraphs_by_heading_marker(paragraphs):
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

def extract_epub_to_clean_text():
    # Prepend a special marker paragraph ("#####START_HEADING#####") 
    # before the extracted paragraphs, ensuring a flat list structure.
    paragraphs = [SECTION_HEADER_MARKER] + extract_paragraphs_from_epub()

    save_paragraphs_to_file(paragraphs)

    chapters = split_paragraphs_by_heading_marker(paragraphs)
    save_chapters_to_file(chapters)

    chunks = split_paragraphs_into_chunks(paragraphs)

    save_chunks_to_file(chunks)

# Example usage
if __name__ == "__main__":
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    base_dir_epub = os.path.join(BASE_DIR, "epub")
    base_dir_txt = os.path.join(BASE_DIR, "txt", FILENAME)
    base_dir_mp3 = os.path.join(BASE_DIR, "mp3", FILENAME)

    # Create necessary directories
    os.makedirs(base_dir_txt, exist_ok=True)
    os.makedirs(base_dir_mp3, exist_ok=True)

    EPUB_PATH = os.path.join(base_dir_epub, FILENAME + ".epub")
    PARAGRAPHS_PATH = os.path.join(base_dir_txt, "paragraphs.txt")
    CHAPTERS_PATH = base_dir_txt
    CHUNKS_PATH = os.path.join(base_dir_txt, "chunks.txt")
    MP3_PATH = os.path.join(base_dir_mp3, FILENAME + ".mp3")

    extract_epub_to_clean_text()
    #create_audiobook(chunks_path, mp3_path, voice="en-GB-RyanNeural")

