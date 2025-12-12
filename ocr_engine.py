from paddleocr import PPStructureV3

# PPStructureV3 pipeline parameters:
# ==============================================================================
# INPUT & OUTPUT
# ==============================================================================
# input: (Required) Path to image/PDF, URL, or directory of images.
# save_path: Path to save results. If None, results aren't saved locally.

# ==============================================================================
# LAYOUT DETECTION (Structure Analysis)
# ==============================================================================
# layout_detection_model_name: Name of layout model. Uses default if None.
# layout_detection_model_dir: Local path to layout model. Downloads official if None.
# layout_threshold: (float) Score threshold (0-1). Default: 0.5.
# layout_nms: (bool) Use Non-Maximum Suppression? Default: True.
# layout_unclip_ratio: (float) Box expansion ratio. Default: 1.0.
# layout_merge_bboxes_mode: (str) specific to overlapping boxes. Default: 'large'.
#    - 'large': Keep largest outer box, remove inner.
#    - 'small': Keep smallest inner box, remove outer.
#    - 'union': Keep both.

# ==============================================================================
# MODULE SPECIFIC MODELS (Chart, Region, Doc Orientation)
# ==============================================================================
# chart_recognition_model_name: Name of chart parsing model.
# chart_recognition_model_dir: Path to chart model.
# chart_recognition_batch_size: (int) Batch size for charts. Default: 1.
# region_detection_model_name: Name of region detection model.
# region_detection_model_dir: Path to region detection model.
# doc_orientation_classify_model_name: Name of doc orientation model.
# doc_orientation_classify_model_dir: Path to doc orientation model.
# doc_unwarping_model_name: Name of doc unwarping model.
# doc_unwarping_model_dir: Path to doc unwarping model.

# ==============================================================================
# TEXT DETECTION (OCR - Detection)
# ==============================================================================
# text_detection_model_name: Name of text det model.
# text_detection_model_dir: Path to text det model.
# text_det_limit_side_len: (int) Max image side length. Default: 960.
# text_det_limit_type: (str) 'min' or 'max' side limit. Default: 'max'.
# text_det_thresh: (float) Pixel score threshold for text. Default: 0.3.
# text_det_box_thresh: (float) Box average score threshold. Default: 0.6.
# text_det_unclip_ratio: (float) Expansion ratio. Larger = more area. Default: 2.0.

# ==============================================================================
# TEXT RECOGNITION & ORIENTATION
# ==============================================================================
# textline_orientation_model_name: Name of line orientation model.
# textline_orientation_model_dir: Path to line orientation model.
# textline_orientation_batch_size: (int) Batch size. Default: 1.
# text_recognition_model_name: Name of text rec model.
# text_recognition_model_dir: Path to text rec model.
# text_recognition_batch_size: (int) Batch size. Default: 1.
# text_rec_score_thresh: (float) Min score to keep result. Default: 0.0.

# ==============================================================================
# TABLE RECOGNITION
# ==============================================================================
# table_classification_model_name: Name of table class model.
# table_classification_model_dir: Path to table class model.
# wired_table_structure_recognition_model_name: Wired table structure model name.
# wired_table_structure_recognition_model_dir: Wired table structure model path.
# wireless_table_structure_recognition_model_name: Wireless table structure model name.
# wireless_table_structure_recognition_model_dir: Wireless table structure model path.
# wired_table_cells_detection_model_name: Wired cell det model name.
# wired_table_cells_detection_model_dir: Wired cell det model path.
# wireless_table_cells_detection_model_name: Wireless cell det model name.
# wireless_table_cells_detection_model_dir: Wireless cell det model path.
# table_orientation_classify_model_name: Table orientation model name.
# table_orientation_classify_model_dir: Table orientation model path.

# ==============================================================================
# SEAL (STAMP) RECOGNITION
# ==============================================================================
# seal_text_detection_model_name: Name of seal det model.
# seal_text_detection_model_dir: Path to seal det model.
# seal_det_limit_side_len: (int) Limit side len. Default: 736.
# seal_det_limit_type: (str) 'min' or 'max'. Default: 'min' (Different from text default!).
# seal_det_thresh: (float) Pixel threshold. Default: 0.2.
# seal_det_box_thresh: (float) Box threshold. Default: 0.6.
# seal_det_unclip_ratio: (float) Expansion ratio. Default: 0.5.
# seal_text_recognition_model_name: Name of seal rec model.
# seal_text_recognition_model_dir: Path to seal rec model.
# seal_text_recognition_batch_size: (int) Batch size. Default: 1.
# seal_rec_score_thresh: (float) Min score. Default: 0.0.

# ==============================================================================
# FORMULA RECOGNITION
# ==============================================================================
# formula_recognition_model_name: Name of formula rec model.
# formula_recognition_model_dir: Path to formula rec model.
# formula_recognition_batch_size: (int) Batch size. Default: 1.

# ==============================================================================
# PIPELINE TOGGLES (Enable/Disable Modules)
# ==============================================================================
# use_doc_orientation_classify: (bool) Load doc orientation? Default: False.
# use_doc_unwarping: (bool) Load doc unwarping? Default: False.
# use_textline_orientation: (bool) Load text line orientation? Default: False.
# use_seal_recognition: (bool) Load seal sub-pipeline? Default: False.
# use_table_recognition: (bool) Load table sub-pipeline? Default: True.
# use_formula_recognition: (bool) Load formula sub-pipeline? Default: True.
# use_chart_recognition: (bool) Load chart module? Default: False.
# use_region_detection: (bool) Load region detection? Default: True.

# ==============================================================================
# HARDWARE & PERFORMANCE
# ==============================================================================
# device: (str) 'cpu', 'gpu:0', 'npu:0', 'xpu:0', etc. Defaults to GPU:0 if avail.
# enable_hpi: (bool) Enable High Performance Inference. Default: False.
# use_tensorrt: (bool) Use TensorRT acceleration. Requires compatible model/TRT ver. Default: False.
# precision: (str) 'fp32' or 'fp16'. Default: 'fp32'.
# enable_mkldnn: (bool) Enable MKL-DNN acceleration. Default: True.
# mkldnn_cache_capacity: (int) Cache capacity. Default: 10.
# cpu_threads: (int) Threads for CPU inference. Default: 8.
# paddlex_config: (str) Path to PaddleX pipeline config file.

from config import Config

class OCREngine:
    
    # Example usage for config:
    # config = {
    #    'input': 'path/to/image_or_pdf',
    #    'save_path': 'path/to/save_results',
    #    'layout_detection_model_name': 'lp://PubLayNet/ppyolov2_r50vd_dcn_365e_publaynet',
    # }
    # config is a dict
    def __init__(self, pipeline_config = Config.PIPELINE_DEFAULT_CONFIG):
        """
        Initialize the OCR engine (PPStructureV3 pipeline specifically) with the provided pipeline configuration.
        
        :param pipeline_config: Configuration dictionary for the OCR engine.
        """
        self.pipeline_config = pipeline_config
        
        # Load PPStructureV3 pipeline
        self.ocr_pipeline = PPStructureV3(**pipeline_config)

    def predict(self, input_path, save_path=None):
        """
        Perform OCR prediction on the given input.

        :param input_path: Path to the input image or PDF.
        :param save_path: Optional path to save the results.
        :return: OCR results.
        """
        results = self.ocr_pipeline.predict(input_path)

        if save_path:
            for res in results:
                res.save_to_json(save_path=save_path)
                res.save_to_markdown(save_path=save_path)
        return results

