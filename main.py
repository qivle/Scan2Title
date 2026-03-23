import sys
import logging
from pathlib import Path
from tqdm import tqdm
from colorama import init, Fore, Style
from datetime import datetime
import concurrent.futures
import config
from pdf_converter import pdf_to_images
from ocr_client import PaddleOCRClient
from llm_client import LLMClient
from file_processor import copy_and_rename

init(autoreset=True)
logging.basicConfig(level=logging.INFO, format="%(message)s", handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)

def process_pdf(pdf_path, ocr_client, llm_client):
    try:
        images = pdf_to_images(pdf_path, config.MAX_PAGES_TO_SCAN, config.IMAGE_DPI)
        ocr_results = [r for img in images if (r := ocr_client.recognize(img))]
        if not ocr_results:
            return None, None, "OCR failed", "", ""
        ocr_text = "\n\n".join(ocr_results)
        info = llm_client.extract_info(ocr_text)
        if not info:
            return None, None, "Extraction failed", ocr_text, ""
        return info.get("title"), info.get("date"), None, ocr_text, info
    except Exception as e:
        return None, None, str(e), "", ""

def process_single_pdf(pdf_path, output_dir, log_file_path):
    """
    处理单个PDF文件
    """
    # 为每个线程创建独立的客户端实例
    ocr_client, llm_client = PaddleOCRClient(), LLMClient()
    
    logger.info(f"Processing: {pdf_path.name}")
    title, date, error, ocr_text, llm_info = process_pdf(pdf_path, ocr_client, llm_client)
    
    # 记录详细信息到日志文件
    with open(log_file_path, 'a', encoding='utf-8') as log_file:
        log_file.write(f"File: {pdf_path.name}\n")
        log_file.write("-" * 40 + "\n")
        
        if error:
            log_file.write(f"Status: FAILED\n")
            log_file.write(f"Error: {error}\n")
            logger.error(f"{Fore.RED}Failed: {error}{Style.RESET_ALL}")
            return False
        else:
            dest_path = copy_and_rename(pdf_path, output_dir, title, date)
            log_file.write(f"Status: SUCCESS\n")
            log_file.write(f"Extracted Title: {title}\n")
            log_file.write(f"Extracted Date: {date}\n")
            log_file.write(f"Final Filename: {dest_path.name}\n")
            logger.info(f"{Fore.GREEN}Success: {dest_path.name}{Style.RESET_ALL}")
            
        if ocr_text:
            log_file.write("OCR Results:\n")
            log_file.write(ocr_text[:1000] + ("..." if len(ocr_text) > 1000 else "") + "\n")
        
        if llm_info:
            log_file.write("LLM Extracted Info: {}".format(llm_info) + "\n")
        
        log_file.write("\n" + "=" * 80 + "\n\n")
        return True

def main():
    input_dir, output_dir = config.INPUT_DIR, config.OUTPUT_DIR
    if not input_dir.exists():
        logger.error("Input directory does not exist")
        sys.exit(1)
    output_dir.mkdir(exist_ok=True)
    pdf_files = list(input_dir.glob("*.pdf"))
    if not pdf_files:
        logger.warning("No PDF files found")
        return
    
    # 创建日志文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file_path = output_dir / f"process_log_{timestamp}.txt"
    
    logger.info(f"Found {len(pdf_files)} PDF files")
    success, fail = 0, 0
    
    # 写入日志文件头
    with open(log_file_path, 'w', encoding='utf-8') as log_file:
        log_file.write(f"Processing started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_file.write(f"Total PDF files: {len(pdf_files)}\n")
        log_file.write("=" * 80 + "\n\n")
    
    # 使用多线程并发处理
    max_workers = 5  # 一次处理5个文件
    logger.info(f"Starting concurrent processing with {max_workers} workers...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        futures = {executor.submit(process_single_pdf, pdf_path, output_dir, log_file_path): pdf_path for pdf_path in pdf_files}
        
        # 跟踪进度
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Processing"):
            pdf_path = futures[future]
            try:
                result = future.result()
                if result:
                    success += 1
                else:
                    fail += 1
            except Exception as e:
                logger.error(f"{Fore.RED}Error processing {pdf_path.name}: {e}{Style.RESET_ALL}")
                fail += 1
    
    # 写入总结
    with open(log_file_path, 'a', encoding='utf-8') as log_file:
        log_file.write(f"Processing completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_file.write(f"Success: {success}, Failed: {fail}\n")
    
    logger.info(f"\n{Fore.CYAN}Complete! Success: {success}, Failed: {fail}{Style.RESET_ALL}")
    logger.info(f"Log file created: {log_file_path}")

if __name__ == "__main__":
    main()