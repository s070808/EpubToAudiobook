import os
import asyncio
import edge_tts
from ebooklib import epub
from bs4 import BeautifulSoup
import math

ITEM_DOCUMENT = 9

MAX_CHARS_PER_REQUEST = 4500  # Edge TTS safe limit

def extract_text_from_epub(epub_path):
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




def split_text_into_chunks(text, max_length):
    paragraphs = text.split('\n')  # assume \n separates logical paragraphs
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue  # skip empty lines

        if len(current_chunk) + len(para) + 1 < max_length:
            current_chunk += para + "\n"
        else:
            chunks.append(current_chunk.strip())
            current_chunk = para + "\n"

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


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
            break





def create_audiobook(epub_path, output_mp3_path, voice="en-US-AriaNeural"):
    paragraphs = extract_text_from_epub(epub_path)

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

    asyncio.run(text_to_mp3(chunks, output_mp3_path, voice))


# Example usage
if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    filename = "Nick_Carter_-_[Killmaster_027]_-_Assignment_Israel"
    epub_path = os.path.join(BASE_DIR, "epub/" + filename+".epub")
    output_path = os.path.join(BASE_DIR, "mp3/" + filename+".mp3")

    create_audiobook(epub_path, output_path, voice="en-GB-RyanNeural")
