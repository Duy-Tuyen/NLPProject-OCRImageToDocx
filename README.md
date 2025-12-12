
# Output folder structure:
output/
├── <page_number>/
│   ├── imgs/
|      ├── img_in_img_box_<block['block_bbox'][0]>_<block['block_bbox'][1]>_<block['block_bbox'][2]>_<block['block_bbox'][3]>.png
       ├── img_in_table_box_<block['block_bbox'][0]>_<block['block_bbox'][1]>_<block['block_bbox'][2]>_<block['block_bbox'][3]>.png
│   ├── <page_number>.md # Ignore for now (used to generate images in imgs/)
    |── <page_number>_improved.json # Improved version of _res.json using ProtonX
    |── <page_number>_res.json # OCR results for the input image
    |── <page_number>_res.docx # Word doc generated from either _res.json, or _improved.json if exists

# CMD Usage:
python main.py --ocr_engine <path_to_input_image>
-> output: output/<page_number>/<page_number>_res.json
Example: python main.py --ocr_engine ./input/483.jpg
-> output: output/483/483_res.json

python main.py --correct_text <path_to_output_folder>
-> output: output/<page_number>/<page_number>_improved.json
Example: python main.py --correct_text ./output/483
-> output: output/483/483_improved.json

python main.py --build_docx <path_to_output_folder>
-> output: output/<page_number>/<page_number>_res.docx (based on _improved.json if exists, else _res.json)
Example: python main.py --build_docx ./output/483
-> output: output/483/483_res.docx