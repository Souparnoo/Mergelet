import io
import os
import sys
import threading
from tkinter import filedialog, messagebox, Listbox, Frame, Scrollbar, Canvas, RIGHT, Y, LEFT, BOTH, END, VERTICAL
import ttkbootstrap as tb
from pypdf import PdfReader, PdfWriter, PageObject
from pdf2image import convert_from_path
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.utils import ImageReader
import os
import sys
import os
import sys

# Function to get base path of the EXE or script
def get_base_path():
    if getattr(sys, 'frozen', False):  # EXE
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

# Set poppler path dynamically
POPPLER_PATH = os.path.join(get_base_path(), "poppler", "bin")

if getattr(sys, 'frozen', False):
    BASE_PATH = sys._MEIPASS
else:
    BASE_PATH = os.path.abspath(".")

# 👇 Fix for EXE: Poppler inside packaged folder
POPPLER_PATH = os.path.join(BASE_PATH, "poppler", "bin")

# ✅ Robust poppler path handling (works in script & PyInstaller exe)
if getattr(sys, 'frozen', False):
    # When running from a PyInstaller bundle
    BASE_PATH = sys._MEIPASS
    POPPLER_PATH = os.path.join(BASE_PATH, "poppler", "bin")
else:
    # When running from .py directly
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))
    POPPLER_PATH = os.path.join(BASE_PATH, "poppler", "bin")

POPPLER_PATH = os.path.abspath(POPPLER_PATH)


merge_listbox_paths = []
# --- Booklet Logic ---
def pad_to_multiple_of_4(reader: PdfReader) -> PdfReader:
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    remainder = len(writer.pages) % 4
    if remainder:
        width = float(reader.pages[0].mediabox.width)
        height = float(reader.pages[0].mediabox.height)
        for _ in range(4 - remainder):
            writer.add_blank_page(width=width, height=height)
    buffer = io.BytesIO()
    writer.write(buffer)
    buffer.seek(0)
    return PdfReader(buffer)

def get_booklet_order(n):
    order = []
    left = 0
    right = n - 1
    while left < right:
        order.append((right, left))     # front
        left += 1
        right -= 1
        order.append((left, right))     # back
        left += 1
        right -= 1
    return order

def merge_pages_to_sheet(left_page_num, right_page_num, reader: PdfReader):
    page_width = float(reader.pages[0].mediabox.width)
    page_height = float(reader.pages[0].mediabox.height)
    new_page = PageObject.create_blank_page(None, page_width * 2, page_height)
    if left_page_num is not None:
        new_page.merge_page(reader.pages[left_page_num])
    if right_page_num is not None:
        new_page.merge_translated_page(reader.pages[right_page_num], tx=page_width, ty=0)
    return new_page

def make_booklet(input_file, output_file, progress_callback=None):
    reader = PdfReader(input_file)
    reader = pad_to_multiple_of_4(reader)
    order = get_booklet_order(len(reader.pages))
    writer = PdfWriter()
    total = len(order)
    for i, (left, right) in enumerate(order):
        merged_page = merge_pages_to_sheet(left, right, reader)
        writer.add_page(merged_page)
        if progress_callback:
            percent = ((i + 1) / total) * 100
            progress_callback(percent)
    with open(output_file, "wb") as f:
        writer.write(f)

# --- Visual Merge Logic with Progress ---
def merge_pdfs_visually_with_progress(input_paths, output_path, total_files, dpi=300):
    all_images = []
    max_width = max_height = 0

    for path in input_paths:
        images = convert_from_path(path, dpi=dpi, poppler_path=POPPLER_PATH)
        all_images.extend(images)
        for img in images:
            w, h = img.size
            max_width = max(max_width, w)
            max_height = max(max_height, h)

    total_pages = len(all_images)
    c = pdf_canvas.Canvas(output_path, pagesize=(max_width, max_height))

    for i, img in enumerate(all_images):
        img_width, img_height = img.size
        scale = min(max_width / img_width, max_height / img_height)
        draw_width = img_width * scale
        draw_height = img_height * scale
        x = (max_width - draw_width) / 2
        y = (max_height - draw_height) / 2
        c.drawImage(ImageReader(img), x, y, width=draw_width, height=draw_height)
        c.showPage()

        percent = ((i + 1) / total_pages) * 100
        progress_bar["value"] = percent
        progress_label.config(text=f"{int(percent)}% complete")
        app.update_idletasks()

    c.save()


# --- Merge PDF Thread ---
def merge_pdfs_action():
    if not merge_listbox_paths:
        messagebox.showerror("Error", "No PDFs selected for merging.")
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".pdf", title="Save Merged PDF As", filetypes=[("PDF files", "*.pdf")])
    if not file_path:
        return
    progress_bar["value"] = 0
    progress_label.config(text="")
    status_var.set("🔄 Merging...")
    threading.Thread(target=run_merge_in_thread, args=(file_path,)).start()

def run_merge_in_thread(file_path):
    try:
        total_files = len(merge_listbox_paths)
        merge_pdfs_visually_with_progress(merge_listbox_paths, file_path, total_files)
        progress_bar["value"] = 100
        status_var.set("✅ Merged!")
        messagebox.showinfo("Success", f"Merged PDF saved as:\n{file_path}")
    except Exception as e:
        status_var.set("❌ Failed")
        messagebox.showerror("Error", str(e))

# --- GUI Event Handlers ---
def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if file_path:
        entry_var.set(file_path)

def choose_output_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if file_path:
        output_var.set(file_path)

def update_progress(percent):
    progress_bar["value"] = percent
    progress_label.config(text=f"{int(percent)}% complete")
    app.update_idletasks()

def start_booklet_thread():
    threading.Thread(target=generate_booklet).start()

def generate_booklet():
    input_pdf = entry_var.get()
    output_pdf = output_var.get()
    if not input_pdf or not os.path.exists(input_pdf):
        messagebox.showerror("Error", "Please select a valid PDF file.")
        return
    if not output_pdf:
        messagebox.showerror("Error", "Please choose where to save the booklet.")
        return
    try:
        status_var.set("🔄 Processing...")
        progress_bar["value"] = 0
        update_progress(0)
        make_booklet(input_pdf, output_pdf, update_progress)
        update_progress(100)
        status_var.set("✅ Done!")
        messagebox.showinfo("Success", f"Booklet created:\n{output_pdf}")
    except Exception as e:
        status_var.set("❌ Failed")
        messagebox.showerror("Error", str(e))

def add_pdf_to_merge_list():
    files = filedialog.askopenfilenames(filetypes=[("PDF Files", "*.pdf")])
    for file_path in files:
        if file_path:
            merge_listbox.insert("end", os.path.basename(file_path))
            merge_listbox_paths.append(file_path)

def move_up():
    selected = merge_listbox.curselection()
    for i in selected:
        if i == 0: continue
        merge_listbox_paths[i - 1], merge_listbox_paths[i] = merge_listbox_paths[i], merge_listbox_paths[i - 1]
        text = merge_listbox.get(i)
        merge_listbox.delete(i)
        merge_listbox.insert(i - 1, text)
        merge_listbox.select_set(i - 1)

def move_down():
    selected = list(merge_listbox.curselection())[::-1]
    for i in selected:
        if i == merge_listbox.size() - 1: continue
        merge_listbox_paths[i + 1], merge_listbox_paths[i] = merge_listbox_paths[i], merge_listbox_paths[i + 1]
        text = merge_listbox.get(i)
        merge_listbox.delete(i)
        merge_listbox.insert(i + 1, text)
        merge_listbox.select_set(i + 1)

def delete_selected_pdf():
    selected = list(merge_listbox.curselection())[::-1]
    for i in selected:
        merge_listbox.delete(i)
        del merge_listbox_paths[i]

def delete_all_pdfs():
    merge_listbox.delete(0, END)
    merge_listbox_paths.clear()

# --- GUI Layout ---
app = tb.Window(themename="superhero")
app.title("📘 PDF Booklet & Merger")
app.geometry("600x500")
app.resizable(True, True)

gui_canvas = Canvas(app)
scrollbar = Scrollbar(app, orient=VERTICAL, command=gui_canvas.yview)
gui_canvas.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side=RIGHT, fill=Y)
gui_canvas.pack(side=LEFT, fill=BOTH, expand=True)

scrollable_frame = Frame(gui_canvas)
scrollable_frame.bind("<Configure>", lambda e: gui_canvas.configure(scrollregion=gui_canvas.bbox("all")))
gui_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
scrollable_frame.bind_all("<MouseWheel>", lambda e: gui_canvas.yview_scroll(-1 * int(e.delta / 120), "units"))

entry_var = tb.StringVar()
output_var = tb.StringVar()
status_var = tb.StringVar(value="📘 Ready")

tb.Label(scrollable_frame, text="📄 Select PDF File for Booklet:", font=("Segoe UI", 11)).pack(pady=(10, 5))
tb.Entry(scrollable_frame, textvariable=entry_var, width=60).pack()
tb.Button(scrollable_frame, text="Browse PDF", bootstyle="info-outline", command=browse_file).pack(pady=2)

tb.Label(scrollable_frame, text="💾 Save Booklet As:", font=("Segoe UI", 11)).pack(pady=(10, 5))
tb.Entry(scrollable_frame, textvariable=output_var, width=60).pack()
tb.Button(scrollable_frame, text="Choose Output Location", bootstyle="primary-outline", command=choose_output_file).pack(pady=2)

tb.Button(scrollable_frame, text="🛠️ Create Booklet", bootstyle="success", command=start_booklet_thread).pack(pady=10)

progress_label = tb.Label(scrollable_frame, text="", font=("Segoe UI", 10))
progress_label.pack()
progress_bar = tb.Progressbar(scrollable_frame, length=400, mode='determinate')
progress_bar.pack(pady=5)
tb.Label(scrollable_frame, textvariable=status_var, font=("Segoe UI", 10, "italic")).pack(pady=(5, 10))

tb.Label(scrollable_frame, text="📚 Merge Multiple PDFs (Reorderable):", font=("Segoe UI", 11)).pack(pady=5)

merge_frame = Frame(scrollable_frame)
merge_frame.pack(pady=5)
scrollbar_merge = Scrollbar(merge_frame)
scrollbar_merge.pack(side=RIGHT, fill=Y)

merge_listbox = Listbox(merge_frame, width=80, height=7, selectmode="extended", yscrollcommand=scrollbar_merge.set)
merge_listbox.pack(side=LEFT, fill=BOTH)
scrollbar_merge.config(command=merge_listbox.yview)

merge_listbox.bind("<MouseWheel>", lambda e: merge_listbox.yview_scroll(-1 * int(e.delta / 120), "units"))
tb.Button(scrollable_frame, text="➕ Add PDFs", bootstyle="info-outline", command=add_pdf_to_merge_list).pack(pady=2)
tb.Button(scrollable_frame, text="🔼 Move Up", bootstyle="secondary-outline", command=move_up).pack(pady=2)
tb.Button(scrollable_frame, text="🔽 Move Down", bootstyle="secondary-outline", command=move_down).pack(pady=2)
tb.Button(scrollable_frame, text="❌ Delete Selected", bootstyle="danger-outline", command=delete_selected_pdf).pack(pady=2)
tb.Button(scrollable_frame, text="🗑️ Clear All", bootstyle="danger", command=delete_all_pdfs).pack(pady=2)
tb.Button(scrollable_frame, text="📎 Merge PDFs", bootstyle="success-outline", command=merge_pdfs_action).pack(pady=10)

app.mainloop()
