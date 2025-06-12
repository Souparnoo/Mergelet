# Mergelet 🌀
A simple and powerful PDF merger and booklet generator built with Python and Tkinter.

## 💡 Features
- Merge multiple PDFs
- Reorder pages with drag & drop
- Generate booklet-style PDFs
- Standalone EXE (no installation needed)

## 📷 Screenshots

Here’s what the Mergelet interface looks like:

![Mergelet Interface](https://github.com/Souparnoo/Mergelet/blob/main/Merglet%20Interface.png?raw=true)


## 🛠 Installation
### For Windows
1. Download the `.exe` from [Releases](https://github.com/Souparnoo/Mergelet/releases/tag/v1.0.0).
2. Double-click to run!

### For Developers
```bash
git clone https://github.com/Souparnoo/Mergelet.git
cd Mergelet
pip install -r requirements.txt
python main.py
```
## ⚙️ Technologies Used

- **Python 3.10+** – Core programming language
- **Tkinter** – GUI framework for the desktop app
- **PyPDF2** – PDF manipulation (merge, page extraction)
- **Pillow (PIL)** – Image handling (for preview/thumbnail if added)
- **PyInstaller** – Packaging into `.exe` for Windows

## ✨ Features

- 📎 **Merge PDFs**: Combine any number of PDF files into a single document.
- 📐 **Uniform Resolution**: Output PDF maintains consistent resolution, regardless of input file differences.
- 🔃 **Drag and Drop Reordering**: Rearrange files visually with ease.
- 📖 **Booklet Generation**:
  - Automatic arrangement of pages into a printable booklet format.
  - Automatically adds blank pages to make the total count a multiple of 4.
- 🧳 **Portable**: Single `.exe` file, no installation required.
- 🪄 **Clean Interface**: Simple, intuitive GUI that works out-of-the-box.

## 🔧 Basic Logic Behind the App

### 🧷 Merging PDFs
- Reads all selected PDF files.
- Extracts and appends each page sequentially.
- Ensures output PDF has a consistent DPI and page size.

### 📖 Booklet Arrangement Logic
Booklet mode arranges pages such that when printed double-sided and folded, the order is correct.

Steps:
1. Ensure total page count is a multiple of 4 by adding blank pages.
2. Apply this pattern:
   - Page pairs: `(n-1, 0)`, `(1, n-2)`, `(2, n-3)`, ...
   - Continue pairing from outermost to innermost pages.
3. Rearranged pairs are merged into output for booklet printing.

This mimics how physical booklets are printed on sheets that are folded in the middle.

## 🙏 Credits

- Developed by [Souparna](https://github.com/Souparnoo)
- Special thanks to [ChatGPT](https://openai.com/chatgpt) by OpenAI for guidance, logic refinement, and documentation assistance ✨

## 📜 License
MIT – free to use, modify, and distribute.
