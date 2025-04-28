import os
import asyncio
import edge_tts
from ebooklib import epub
from bs4 import BeautifulSoup
import math
import re  # Used for matching chapter filenames like _chapter_0001.txt

# Constants for parsing and formatting
ITEM_DOCUMENT = 9
SECTION_HEADER_MARKER = '#####START_HEADING#####'
CHUNK_MARKER = '#####CHUNK#####'
MAX_CHUNK_SIZE = 4000  # Maximum number of characters per text chunk (edge_tts API limit)

# File and folder paths (they will be filled later)
FILENAME = "Nick_Carter_-_[Killmaster_027]_-_Assignment_Israel"
EPUB_PATH = ''
CHAPTERS_PATH = ''
MP3_PATH = ''

CHAPTER_KEY = '_chapter_'  # Used to prefix chapter filenames


def emphasize_headings(soup):
    """Replace all heading tags (h1-h6) in HTML with a special marker line."""
    for level in range(1, 7):  # For heading levels 1 to 6
        for tag in soup.find_all(f'h{level}'):
            heading_text = tag.get_text(strip=True)
            new_string = f"{SECTION_HEADER_MARKER}{heading_text}\n"
            tag.replace_with(new_string)


def extract_paragraphs_from_epub():
    """Extract all clean paragraphs from the EPUB file."""
    book = epub.read_epub(EPUB_PATH)
    paragraphs = []

    for item in book.get_items():
        if item.get_type() == ITEM_DOCUMENT:  # Only process document items
            soup = BeautifulSoup(item.get_content(), 'html.parser')

            # Remove unwanted HTML tags
            for tag in soup.find_all(['script', 'style', 'head', 'title', 'meta', '[document]']):
                tag.decompose()

            # Mark headings clearly
            emphasize_headings(soup)

            # Get visible text parts
            texts = soup.stripped_strings  # Generator of clean text nodes

            for text in texts:
                clean_text = ' '.join(text.split())  # Normalize spacing
                if clean_text:
                    paragraphs.append(clean_text)

    return paragraphs


async def text_to_mp3(text_chunks, output_path, voice="en-US-AriaNeural"):
    """Convert a list of text chunks to an MP3 audio file using edge_tts."""
    with open(output_path, 'wb') as out_f:
        total_chunks = len(text_chunks)
        for idx, chunk in enumerate(text_chunks, 1):
            print(f"\n=== Processing chunk {idx}/{total_chunks} ===")
            print(chunk)
            print("\n=== End of chunk ===\n")

            communicate = edge_tts.Communicate(text=chunk, voice=voice)

            # Stream the TTS output and write all audio data
            async for chunk_data in communicate.stream():
                if chunk_data["type"] == "audio":
                    out_f.write(chunk_data["data"])
            # No break! (important) — we let all chunks render


def load_chunks_from_file(output_path):
    """Load text chunks from a file (used if working with pre-saved chunks)."""
    with open(output_path, 'r', encoding='utf-8') as f:
        content = f.read()

    chunks = content.split(CHUNK_MARKER)
    chunks = [chunk for chunk in chunks if chunk != '']

    return chunks


def split_paragraphs_into_chunks(paragraphs):
    """Split paragraphs into manageable text chunks based on maximum size."""
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        # +2 because of the two newline characters added between paragraphs
        if len(current_chunk) + len(para) + 2 < MAX_CHUNK_SIZE:
            current_chunk += para + "\n\n"
        else:
            chunks.append(current_chunk.rstrip("\n\n"))
            current_chunk = para + "\n\n"

    if current_chunk:
        chunks.append(current_chunk.rstrip("\n\n"))

    return chunks


def save_chapters_to_file(chapters):
    """Save each chapter as a separate text file with padded numbering."""
    for i, chap in enumerate(chapters):
        path = os.path.join(CHAPTERS_PATH, f'{CHAPTER_KEY}{i:04d}.txt')  # Pad chapter numbers like 0001
        with open(path, 'w', encoding='utf-8') as f:
            for para in chap:
                cleaned_para = para.replace(SECTION_HEADER_MARKER, '').strip()
                if cleaned_para:
                    f.write(cleaned_para)
                    f.write("\n\n")  # Double newlines between paragraphs


def split_paragraphs_by_heading_marker(paragraphs):
    """Split the list of paragraphs into chapters based on heading markers."""
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
    """Main flow: extract paragraphs from EPUB and save chapters and full text."""
    # Force a starting heading so the whole book is handled cleanly
    paragraphs = [SECTION_HEADER_MARKER] + extract_paragraphs_from_epub()

    # Split and save into chapter files
    chapters = split_paragraphs_by_heading_marker(paragraphs)
    save_chapters_to_file(chapters)


def load_chapter_files(chapters_path):
    """Find and return a sorted list of chapter text files."""
    chapter_files = []
    for filename in sorted(os.listdir(chapters_path)):
        if re.match(r'_chapter_\d+\.txt$', filename):
            full_path = os.path.join(chapters_path, filename)
            chapter_files.append(full_path)
    return chapter_files


def load_paragraphs_from_file(file_path):
    """Load paragraphs from a saved chapter file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    # Split on double newlines and remove any empty entries
    paragraphs = [para.strip() for para in content.split("\n\n") if para.strip()]
    return paragraphs


async def process_all_chapters_to_mp3():
    """Loop through all chapter files and generate one MP3 file per chapter."""
    chapter_files = load_chapter_files(CHAPTERS_PATH)

    for chapter_file in chapter_files:
        print(f"Processing {chapter_file}...")

        # Load the paragraphs from file
        paragraphs = load_paragraphs_from_file(chapter_file)
        # Split paragraphs into chunks suitable for TTS
        chunks = split_paragraphs_into_chunks(paragraphs)

        # Extract chapter number from filename, e.g., "_chapter_0001.txt" -> 1
        chapter_num = int(os.path.splitext(os.path.basename(chapter_file))[0].split("_")[-1])

        # Build output MP3 path with padded chapter number
        output_mp3_path = os.path.join(MP3_PATH, f"chapter_{chapter_num:04d}.mp3")

        os.makedirs(MP3_PATH, exist_ok=True)  # Ensure MP3 folder exists

        # Actually synthesize and save MP3
        await text_to_mp3(chunks, output_mp3_path, voice="en-US-AriaNeural")


def preamble():
    global EPUB_PATH, CHAPTERS_PATH, MP3_PATH  # Tell Python we are modifying the global vars

    # Set base paths relative to the script location
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    base_dir_epub = os.path.join(BASE_DIR, "epub")
    base_dir_txt = os.path.join(BASE_DIR, "txt", FILENAME)
    base_dir_mp3 = os.path.join(BASE_DIR, "mp3", FILENAME)

    # Make sure output directories exist
    os.makedirs(base_dir_txt, exist_ok=True)
    os.makedirs(base_dir_mp3, exist_ok=True)

    # Now define global paths
    EPUB_PATH = os.path.join(base_dir_epub, FILENAME + ".epub")
    CHAPTERS_PATH = base_dir_txt
    MP3_PATH = base_dir_mp3


if __name__ == "__main__":
    preamble()

    # Extract text and chapters from EPUB
    extract_epub_to_clean_text()

    # Convert all chapters into MP3s
    asyncio.run(process_all_chapters_to_mp3())
