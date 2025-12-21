import logging
import os
import argparse
from tqdm import tqdm

def suppress_logs():
    logging.getLogger('paddleocr').setLevel(logging.ERROR) # Suppress logs from paddleocr except errors
    logging.getLogger('ppstructure').setLevel(logging.ERROR) # Suppress logs from ppstructure except errors
    logging.getLogger('paddlex').setLevel(logging.ERROR) # Suppress logs from paddlex except errors
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3" # Suppress logs from TensorFlow except errors; 3 means ERROR

from utils.timer import Timer, Time
from config import Config
from ocr_engine import OCREngine
from text_correction import TextCorrector
from docx_builder import DOCXBuilder, build_docx_from_ocr_json

import json

from paddleocr import PPStructureV3

# Class for output folder management
# Structure:
# output/[page_number]/[page_number]/
# - imgs/
# - [page_number]_res.json
# - [page_number]_improved.json
# - [page_number]_result.docx
# - [page_number].md (ignore for now)

class OutputPageFolder:

    def __init__(self, base_output_dir: str, page_number: str):
        self.base_output_dir = base_output_dir
        self.page_number = page_number
        self.page_output_dir = os.path.join(base_output_dir, page_number)

        self.imgs_dir = os.path.join(self.page_output_dir, "imgs")
        self.res_json_path = os.path.join(self.page_output_dir, f"{page_number}_res.json")
        self.improved_json_path = os.path.join(self.page_output_dir, f"{page_number}_improved.json")
        self.docx_path = os.path.join(self.page_output_dir, f"{page_number}_result.docx")
        self.md_path = os.path.join(self.page_output_dir, f"{page_number}.md")

        self._create_dirs()

    def _create_dirs(self):
        os.makedirs(self.imgs_dir, exist_ok=True)
        os.makedirs(self.page_output_dir, exist_ok=True)

def ocr_cli(input_image_path: str, save_path: str):
    timer = Timer(name="Initialize OCR engine timer")
    timer.start()
    ocr_engine = OCREngine()
    timer.stop()
    print(f"OCR engine initialized in {timer.runtime}")

    timer = Timer(name="OCR prediction timer")
    timer.start()
    ocr_engine.predict(input_image_path, save_path=save_path)
    timer.stop()
    print(f"OCR prediction completed in {timer.runtime}")

def correct_text_cli(input_json_path: str, save_path: str):
    timer = Timer(name="Initialize text corrector timer")
    timer.start()
    text_corrector = TextCorrector()
    timer.stop()
    print(f"Initialized Text Corrector in {timer.runtime}")

    timer = Timer(name="Text correction timer")
    timer.start()
    text_corrector.improve_json(input_json_path, save_path)
    timer.stop()
    print(f"Text correction completed in {timer.runtime}")

# Mass conversion pipeline:
# 1. Input: folder with images or PDFs (input); each file named as <page_number>.jpg
# 2. For each file:
#  a. Create output folder structure: OutputPageFolder("output", page_number)
#  b. OCR: ocr_cli(input_image_path, save_path)
#  c. Text correction: correct_text_cli(input_json_path, save_path)
#  d. Build DOCX: build_docx_from_ocr_json(res_path, save_path)
def mass_conversion(input_folder: str, output_base_folder: str, min_page_number: int = None, max_page_number: int = None):
    # Create only 1 pipeline instances to save time
    ocr_engine = OCREngine()
    text_corrector = TextCorrector()

    # Get list of files to process
    files_to_process = []
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.pdf')):
            page_number = os.path.splitext(filename)[0]
            
            if min_page_number is not None and int(page_number) < min_page_number:
                continue
            if max_page_number is not None and int(page_number) > max_page_number:
                continue
            
            files_to_process.append(filename)
    
    # Create progress bar
    print(f"\nStarting mass conversion of {len(files_to_process)} files...\n")
    pbar = tqdm(files_to_process, desc="Processing files", unit="file", ncols=100, colour='green')
    
    for filename in pbar:
        page_number = os.path.splitext(filename)[0]
        input_image_path = os.path.join(input_folder, filename)
        output_folder = OutputPageFolder(base_output_dir=output_base_folder, page_number=page_number)

        pbar.set_description(f"Processing page {page_number}")
        timer = Timer()
        timer.start()

        # Step 1: OCR
        pbar.set_postfix_str("OCR...")
        ocr_timer = Timer()
        ocr_timer.start()
        ocr_engine.predict(input_image_path, save_path=output_folder.page_output_dir)
        ocr_timer.stop()
        
        # Step 2: Text Correction
        pbar.set_postfix_str("Correcting text...")
        correction_timer = Timer()
        correction_timer.start()
        text_corrector.improve_json(input_json=output_folder.res_json_path, output_json=output_folder.improved_json_path)
        correction_timer.stop()
        
        # Step 3: Build DOCX
        pbar.set_postfix_str("Building DOCX...")
        build_docx_from_ocr_json(res_path=output_folder.page_output_dir, save_path=output_folder.docx_path)

        timer.stop()
        pbar.set_postfix_str(f"Done ({timer.runtime})")
    
    pbar.close()
    print(f"\n{'='*100}")
    print(f"Mass conversion completed successfully!")
    print(f"Processed {len(files_to_process)} files.")
    print(f"{'='*100}\n")

def main():
    parser = argparse.ArgumentParser(
        description="OCR Image to DOCX (only text for now) using PPStructureV3 pipeline & ProtonX correction",
        formatter_class=argparse.RawDescriptionHelpFormatter # Preserve newlines in help text
    )

    # Argument:
    # --ocr_image <path_to_image>
    # --correct_text <path_to_page_folder>
    # --build_docx <path_to_page_folder>

    parser.add_argument('--ocr_image', type=str, help='Path to the input image or PDF for OCR processing.')
    parser.add_argument('--correct_text', type=str, help='Path to the page folder containing OCR JSON results for text correction.')
    parser.add_argument('--build_docx', type=str, help='Path to the page folder containing OCR JSON results to build DOCX.')
    # mass conversion: --mass_convert <input_folder> <min_page_number> <max_page_number>

    parser.add_argument('--mass_convert',
                        nargs=3,
                        metavar=('input_folder', 'min_page_number', 'max_page_number'),
                        help='Mass convert all images/PDFs in the input folder. Optionally specify min and max page numbers to process.'
    )
    
    parser.add_argument('--mass_build_docx',
                        nargs=2,
                        metavar=('min_page_number', 'max_page_number'),
                        help='Mass build DOCX files from existing JSON in output folder. Specify min and max page numbers.'
    )

    args = parser.parse_args()

    #suppress_logs()

    if args.ocr_image:
        page_number = os.path.splitext(os.path.basename(args.ocr_image))[0]
        output_folder = OutputPageFolder(base_output_dir="output", page_number=page_number)

        ocr_cli(input_image_path=args.ocr_image, save_path=output_folder.page_output_dir)

        print(f"OCR results saved to: {output_folder.page_output_dir}")

    if args.correct_text:
        page_number = os.path.basename(args.correct_text.rstrip(os.sep))
        output_folder = OutputPageFolder(base_output_dir="output", page_number=page_number)

        correct_text_cli(input_json_path=output_folder.res_json_path, save_path=output_folder.improved_json_path)

        print(f"Corrected text JSON saved to: {output_folder.improved_json_path}")
    
    if args.build_docx:
        page_number = os.path.basename(args.build_docx.rstrip(os.sep))
        output_folder = OutputPageFolder(base_output_dir="output", page_number=page_number)

        build_docx_from_ocr_json(res_path=output_folder.page_output_dir, save_path=output_folder.docx_path)

        print(f"DOCX file saved to: {output_folder.docx_path}")

    if args.mass_convert:
        mass_conversion(input_folder=args.mass_convert[0], output_base_folder="output", min_page_number=int(args.mass_convert[1]), max_page_number=int(args.mass_convert[2]))

        print(f"Mass conversion completed. Check the 'output' folder for results.")
    
    if args.mass_build_docx:
        min_page = int(args.mass_build_docx[0])
        max_page = int(args.mass_build_docx[1])
        
        print(f"\nBuilding DOCX files for pages {min_page} to {max_page}...")
        pbar = tqdm(range(min_page, max_page + 1), desc="Building DOCX", unit="file", ncols=100, colour='blue')
        
        ocr_engine = OCREngine()  # Initialize once


        for page_num in pbar:
            page_number = str(page_num)
            output_folder = OutputPageFolder(base_output_dir="output", page_number=page_number)
            
            # Check if JSON exists
            json_path = output_folder.improved_json_path if os.path.exists(output_folder.improved_json_path) else output_folder.res_json_path
            
            if not os.path.exists(json_path):
                pbar.set_postfix_str(f"Skipped (no JSON)")
                continue
            
            try:
                pbar.set_postfix_str(f"Building...")
                build_docx_from_ocr_json(res_path=output_folder.page_output_dir, save_path=output_folder.docx_path, ocr_engine=ocr_engine)
                pbar.set_postfix_str(f"Done")
            except Exception as e:
                pbar.set_postfix_str(f"Error: {str(e)[:30]}")
        
        pbar.close()
        print(f"\nMass DOCX build completed. Check the 'output' folder for results.")


if __name__ == "__main__":
    main()