
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
                num_beams=10,
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

    def improve_json(self, input_json: str, output_json: str):
        try:
            with open(input_json, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for block in data.get('parsing_res_list', []):
                original_text = block.get('block_content', '')

                timer = Timer()
                timer.start()

                if block.get('block_label') == 'table':
                    # original_text here is HTML table
                    # only correct text inside <td>...</td>
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(original_text, 'html.parser')
                    td_tags = soup.find_all('td')
                    for td in td_tags:
                        cell_text = td.get_text()
                        corrected_cell_text = self.correct_text(cell_text)
                        td.string = corrected_cell_text

                    corrected_text = str(soup)
                else:
                    corrected_text = self.correct_text(original_text)
                    
                block['block_content'] = corrected_text

                timer.stop()
                print(f"\nText correction time for block: \n\t{timer.runtime}\n")

            with open(output_json, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

        except Exception as e:
            print(f"Error improving JSON: {e}")

