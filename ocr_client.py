import logging
import httpx
import base64
import json
import config

logger = logging.getLogger(__name__)

class PaddleOCRClient:
    def __init__(self):
        self.api_key = config.SILICONFLOW_API_KEY
        self.base_url = config.SILICONFLOW_BASE_URL
        self.model = config.OCR_MODEL
    
    def recognize(self, image_bytes: bytes):
        """
        使用云端 PaddleOCR-VL-1.5 识别图片文字
        """
        max_retries = 3  # 最多重试3次（包括第一次）
        retry_delay = 2  # 重试间隔（秒）
        
        for retry in range(max_retries):
            try:
                # 将图片转换为 base64
                image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                
                # 构建 API 请求
                url = f"{self.base_url}/chat/completions"
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                # PaddleOCR-VL-1.5 提示词
                prompt = "请识别图片中的所有文字，返回完整文本内容。"
                
                payload = {
                    "model": self.model,
                    "messages": [{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
                        ]
                    }],
                    "temperature": 0.1,
                    "max_tokens": 1000
                }
                
                # 发送请求
                response = httpx.post(url, json=payload, headers=headers, timeout=config.REQUEST_TIMEOUT)
                response.raise_for_status()
                
                # 解析响应
                content = response.json()['choices'][0]['message']['content']
                
                logger.info(f"OCR 识别成功 (重试 {retry+1}/{max_retries})")
                return content
                
            except Exception as e:
                logger.error(f"OCR 识别失败 (重试 {retry+1}/{max_retries})：{e}")
                if retry < max_retries - 1:
                    import time
                    logger.info(f"等待 {retry_delay} 秒后重试...")
                    time.sleep(retry_delay)
                else:
                    return None