import os
import asyncio
import edge_tts
from ebooklib import epub
from bs4 import BeautifulSoup
import math

ITEM_DOCUMENT = 9

MAX_CHARS_PER_REQUEST = 4500  # Edge TTS safe limit

def extract_paragraphs_from_epub(epub_path):
    book = epub.read_epub(epub_path)
    paragraphs = []

    for item in book.get_items():
        if item.get_type() == 9:  # ITEM_DOCUMENT
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            
            # Remove unwanted elements (style, script, head, etc.)
            for tag in soup(['script', 'style', 'head', 'title', 'meta', '[document]']):
                tag.decompose()

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
            #break - use to debug rendering, only creates a single chunk


def load_chunks_from_file(output_path):
    with open(output_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split based on the exact separator
    chunks = content.split("\n\n===\n\n")

    # Only remove empty chunks caused by extra separators, but DO NOT strip user content
    chunks = [chunk for chunk in chunks if chunk != '']

    return chunks


def create_audiobook(chunks_path, output_mp3_path, voice="en-US-AriaNeural"):
    chunks = load_chunks_from_file(chunks_path)
    asyncio.run(text_to_mp3(chunks, output_mp3_path, voice))


def extract_epub_to_clean_text (epub_path, output_path):
    paragraphs = extract_paragraphs_from_epub(epub_path)

    # Combine paragraphs carefully into bigger chunks (still <=4500 chars)
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        if len(current_chunk) + len(para) + 1 < 4500:
            current_chunk += para + "\n"
        else:
            chunks.append(current_chunk.strip())
            current_chunk = para + "\n"

    if current_chunk:
        chunks.append(current_chunk.strip())
    
    # Write chunks to output_path
    with open(output_path, 'w', encoding='utf-8') as f:
        for chunk in chunks:
            f.write(chunk)
            f.write("\n\n===\n\n")  # optional separator between chunks

# Example usage
if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    filename = "Nick_Carter_-_[Killmaster_027]_-_Assignment_Israel"
    epub_path = os.path.join(BASE_DIR, "epub/" + filename+".epub")
    chunks_path = os.path.join(BASE_DIR, "txt/" + filename+".txt")
    mp3_path = os.path.join(BASE_DIR, "mp3/" + filename+".mp3")

    extract_epub_to_clean_text(epub_path, chunks_path)
    #create_audiobook(chunks_path, mp3_path, voice="en-GB-RyanNeural")
