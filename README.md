
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

Install or update pip:

```bash
python -m pip install --upgrade pip
```


Install dependencies via pip:

```bash
pip install edge-tts ebooklib beautifulsoup4
```

---

## 🚀 Usage

1. Place your `.epub` file in the sub-folder `/epub/` related to the script.

2. Update the filename at the top of the script, in the "const" value:

```python
FILENAME = "your_epub_filename_without_extension"
```

Example:

```python
FILENAME = "Nick_Carter_-_[Killmaster_027]_-_Assignment_Israel"
```

3. Run the script:

```bash
python epubaudio.py
```

It will generate several MP3 files, one for each chapter, like:

```
/mp3/{FILENAME}/chapter_0000.mp3
/mp3/{FILENAME}/chapter_0001.mp3
/mp3/{FILENAME}/chapter_0002.mp3
etc
```

---

## 🎙️ Choosing a Different Voice (unsupported for now)

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

- **Creates a file for each chapter**: Denoted by <hx> tags
- **Creates an mp3**: For each chapter, in a subfolder denoted by the FILENAME variable

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
