
# Official packages
import os
import json
from typing import List, Dict, Any, Optional, Tuple, Union
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Custom packages
from config import Config
from utils.timer import Timer, Time

# ProtonX
from protonx import ProtonX
#os.environ["PROTONX_API_KEY"] = Config.PROTONX_USER_TOKEN

class TextCorrector:
    def __init__(self,
                 model_path: Optional[str] = Config.PROTONX_CORRECTION_MODEL,
                 max_tokens: Optional[int] = Config.PROTONX_CORRECTION_MAX_TOKENS):
        self.model_path = model_path
        self.max_tokens = max_tokens
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.tokenizer = None
        self.model = None

        self._load_model()
        
    def _load_model(self):
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_path)

            self.model.to(self.device)
            self.model.eval()

        except Exception as e:
            print(f"Error loading Text Correction model: {e}")
            self.tokenizer = None
            self.model = None

    def correct_text(self, text: str) -> str:
        if self.tokenizer is None or self.model is None:
            raise ValueError("Model or tokenizer not loaded properly.")

        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=self.max_tokens
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                num_beams=3,
                num_return_sequences=1,
                max_new_tokens=self.max_tokens,
                early_stopping=True,
                return_dict_in_generate=True,
                output_scores=True
            )

        sequences = outputs.sequences
        scores = outputs.sequences_scores

        for i, (seq, score) in enumerate(zip(sequences, scores)):
            decoded = self.tokenizer.decode(seq, skip_special_tokens=True)

        return decoded

    def correct_texts_batch(self, texts: List[str]) -> List[str]:
        """Correct multiple texts in a single batch for better performance."""
        if self.tokenizer is None or self.model is None:
            raise ValueError("Model or tokenizer not loaded properly.")
        
        if not texts:
            return []
        
        # Tokenize all texts at once
        inputs = self.tokenizer(
            texts,
            return_tensors="pt",
            truncation=True,
            max_length=self.max_tokens,
            padding=True
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                num_beams=3,
                num_return_sequences=1,
                max_new_tokens=self.max_tokens,
                early_stopping=True
            )
        
        # Decode all outputs
        decoded_texts = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)
        return decoded_texts

    def improve_json(self, input_json: str, output_json: str):
        try:
            with open(input_json, 'r', encoding='utf-8') as f:
                data = json.load(f)

            timer = Timer()
            timer.start()

            # Collect all texts to correct in batches
            texts_to_correct = []
            block_indices = []  # Track which block each text belongs to
            table_cell_info = []  # Track table cell positions for reconstruction

            for idx, block in enumerate(data.get('parsing_res_list', [])):
                original_text = block.get('block_content', '')

                if block.get('block_label') == 'table':
                    # Extract all table cell texts for batch processing
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(original_text, 'html.parser')
                    td_tags = soup.find_all('td')
                    
                    for td in td_tags:
                        cell_text = td.get_text()
                        if cell_text.strip():  # Only process non-empty cells
                            texts_to_correct.append(cell_text)
                            table_cell_info.append((idx, td))
                else:
                    if original_text.strip():  # Only process non-empty content
                        texts_to_correct.append(original_text)
                        block_indices.append(idx)

            # Batch process all texts
            if texts_to_correct:
                print(f"Correcting {len(texts_to_correct)} text segments in batch...")
                corrected_texts = self.correct_texts_batch(texts_to_correct)

                # Apply corrections back to blocks
                correction_idx = 0
                
                # Handle table cells
                for block_idx, td in table_cell_info:
                    td.string = corrected_texts[correction_idx]
                    correction_idx += 1
                
                # Reconstruct tables
                table_blocks = {}
                for block_idx, td in table_cell_info:
                    if block_idx not in table_blocks:
                        block = data['parsing_res_list'][block_idx]
                        original_text = block.get('block_content', '')
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(original_text, 'html.parser')
                        table_blocks[block_idx] = soup
                
                for block_idx, soup in table_blocks.items():
                    data['parsing_res_list'][block_idx]['block_content'] = str(soup)
                
                # Handle regular text blocks
                for idx in block_indices:
                    data['parsing_res_list'][idx]['block_content'] = corrected_texts[correction_idx]
                    correction_idx += 1

            timer.stop()
            print(f"Total correction time: {timer.elapsed():.2f}s")

            with open(output_json, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

        except Exception as e:
            print(f"Error improving JSON: {e}")

