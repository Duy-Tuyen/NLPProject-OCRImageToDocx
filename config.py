import os
#import dotenv
#dotenv.load_dotenv('.env')

class Config:

    # Language
    LANGUAGE = 'vi'

    # Document orientation classification model
    USE_DOC_ORIENTATION_CLASSIFY = False
    # Document unwarping module
    USE_DOC_UNWARPING = False
    # Textline orientation classification model
    USE_TEXTLINE_ORIENTATION = False

    # Device for model inference: "cpu" or "gpu"
    DEVICE = "gpu"

    # Pipeline config default dict
    PIPELINE_DEFAULT_CONFIG = {
        'lang': LANGUAGE,
        'device': DEVICE
    }

    # ProtonX section
    ## API key for ProtonX services (not needed for now)
    #PROTONX_USER_TOKEN = os.getenv("PROTONX_USER_TOKEN")
    ## Correction model
    PROTONX_CORRECTION_MODEL = "protonx-models/protonx-legal-tc"
    ## Max tokens for correction model
    PROTONX_CORRECTION_MAX_TOKENS = 160
    
    # Gemini API section
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Set via environment variable
    GEMINI_MODEL = "gemini-2.0-flash"  # Default model for OCR
