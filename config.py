from pathlib import Path

BASE_DIR = Path(__file__).parent
SILICONFLOW_API_KEY = "XXX"  # 填入你的 API Key
SILICONFLOW_BASE_URL = "https://api.siliconflow.cn/v1"
OCR_MODEL = "PaddlePaddle/PaddleOCR-VL-1.5"
LLM_MODEL = "Qwen/Qwen2.5-7B-Instruct"
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
LOG_DIR = BASE_DIR / "logs"
MAX_PAGES_TO_SCAN = 1  # 只扫描第一页
IMAGE_DPI = 150  # 进一步减小 DPI 以减小文件大小
REQUEST_TIMEOUT = 60