# OCR Image to Formatted Dataset

## Output Folder Structure

```
output/
├── <page_number>/
│   ├── imgs/
│   │   ├── img_in_img_box_<block['block_bbox'][0]>_<block['block_bbox'][1]>_<block['block_bbox'][2]>_<block['block_bbox'][3]>.png
│   │   └── img_in_table_box_<block['block_bbox'][0]>_<block['block_bbox'][1]>_<block['block_bbox'][2]>_<block['block_bbox'][3]>.png
│   ├── <page_number>.md
│   ├── <page_number>_improved.json
│   ├── <page_number>_res.json
│   └── <page_number>_res.docx
```
Note: Need input image to be named as `<page_number>.jpg` in the input folder.


### File Descriptions

- **`imgs/`** – Contains extracted images from the document
  - `img_in_img_box_*` – Images found within image blocks
  - `img_in_table_box_*` – Images found within table blocks
- **`<page_number>.md`** – Markdown intermediate file (ignore for now, used to generate images in `imgs/`)
- **`<page_number>_improved.json`** – Improved version of `_res.json` using ProtonX text correction
- **`<page_number>_res.json`** – Raw OCR results from the input image
- **`<page_number>_res.docx`** – Word document generated from `_improved.json` (or `_res.json` if improved version doesn't exist)

## Usage Commands

### 1. Run OCR Engine

Extract OCR data from an input image:

```bash
python main.py --ocr_engine <path_to_input_image>
```

**Output:** `output/<page_number>/<page_number>_res.json`

**Example:**
```bash
python main.py --ocr_engine ./input/483.jpg
```

### 2. Correct Text

Improve OCR results using text correction:

```bash
python main.py --correct_text <path_to_output_folder>
```

**Output:** `output/<page_number>/<page_number>_improved.json`

**Example:**
```bash
python main.py --correct_text ./output/483
```

### 3. Build DOCX

Generate a formatted Word document from OCR results:

```bash
python main.py --build_docx <path_to_output_folder>
```

**Output:** `output/<page_number>/<page_number>_res.docx` (uses `_improved.json` if available, otherwise `_res.json`)

**Example:**
```bash
python main.py --build_docx ./output/483
```

### 4. Mass Processing pipeline of above 3 steps:
Process multiple images in a folder through all three steps:

```bash
python main.py --mass_convert <path_to_input_folder> <min_page_number> <max_page_number>
```

**Output:** Processed files in `output/<page_number>/` for each image in the specified range.

**Example:**
```bash
python main.py --mass_convert ./input 483 490
```