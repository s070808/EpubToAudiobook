
# 📚 EPUB to Audiobook Converter (Python)

This script converts an `.epub` ebook into a spoken `.mp3` audiobook using Microsoft's Edge TTS voices.

It:
- Extracts paragraphs from an EPUB file.
- Cleans up weird linebreaks and merges natural paragraphs.
- Splits the text into safe-size chunks for TTS API limits (~4500 characters per chunk).
- Converts each chunk into audio and saves the result into a single MP3 file.
- Supports selecting different natural-sounding Microsoft TTS voices (like US, UK, Australian accents, etc.)

---

## 🔧 Requirements

Install dependencies via pip:

```bash
pip install ebooklib beautifulsoup4 edge-tts
```

---

## 🚀 Usage

1. Place your `.epub` file in the same directory as the script.

2. Update the filename at the bottom of the script:

```python
filename = "your_epub_filename_without_extension"
```

Example:

```python
filename = "Nick_Carter_-_[Killmaster_027]_-_Assignment_Israel"
```

3. Run the script:

```bash
python your_script_name.py
```

It will generate an MP3 file like:

```
Nick_Carter_-_[Killmaster_027]_-_Assignment_Israel.mp3
```

in the same folder.

---

## 🎙️ Choosing a Different Voice

You can specify different voices by changing the `voice` parameter in `create_audiobook()`:

Example:

```python
create_audiobook(epub_path, output_path, voice="en-GB-RyanNeural")
```

Some example voices:
- `en-US-AriaNeural` (American female)
- `en-US-GuyNeural` (American male)
- `en-GB-RyanNeural` (British male)
- `en-AU-NatashaNeural` (Australian female)

Full voice list available [here](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support#text-to-speech).

---

## 📜 How It Works

- **Extract paragraphs**: Finds `<p>` tags inside the EPUB HTML, reads their text.
- **Clean text**: Removes unwanted `\n` line breaks inside paragraphs for smooth narration.
- **Chunk text**: Groups paragraphs together until close to the API limit (~4500 characters).
- **TTS Conversion**: Each chunk is streamed to Edge-TTS, audio is saved continuously into a growing MP3 file.

Progress is printed for each chunk processed, so you can track how far the conversion has gone.

---

## ⚡ Known Limitations

- Microsoft Edge-TTS API has ~5000 character per request limit — script automatically chunks to avoid errors.
- Paragraph structure quality depends on the original EPUB formatting (some messy ebooks might need extra cleaning).
- Small pauses between chunks may exist if paragraphs are not naturally merged; future upgrades could use SSML for finer control.

---

## 📦 Future Improvements

- Optional support for multiple output files (1 MP3 per chapter).
- Inject SSML tags for fine control over pause lengths and emphasis.
- Embed metadata (title, author) inside the MP3.
- GUI version for non-technical users.

---

## ✨ Example Output

```bash
=== Processing chunk 1/24 ===
Of the seven Icelandic short stories which appear here, the first was probably written early...
=== End of chunk ===

=== Processing chunk 2/24 ===
The Norsemen who colonized Iceland in the last quarter of the ninth century brought with them...
=== End of chunk ===
```

---

Enjoy making your own audiobooks! 🎧📚
