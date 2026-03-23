import httpx
import logging
import json
import re
import config

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self):
        self.api_key = config.SILICONFLOW_API_KEY
        self.base_url = config.SILICONFLOW_BASE_URL
        self.model = config.LLM_MODEL
    
    def extract_info(self, ocr_text: str):
        max_retries = 3  # 最多重试3次（包括第一次）
        retry_delay = 2  # 重试间隔（秒）
        
        for retry in range(max_retries):
            try:
                prompt = f"""你是一个专业的档案管理专家。请根据以下OCR提取的文本，提取核心信息并按严格的公式生成PDF文件名。

                    【命名公式】
                    项目简称_核心单据名称_补充要素

                    【严格规则】
                    1. 项目简称：提取核心项目名，保持精简,比如出现“广西旅发元境文化旅游开发有限公司”，可简化为“广旅元境”。
                    2. 核心单据名称：必须准确提取（如：开标一览表、用章审批表、投标文件、进度支付申请表、工程款支付证书等），绝不能遗漏！
                    3. 补充要素：如果是支付、请款、计量类文件，**必须提取“第X期”或金额前6位**作为区分，防止文件重名。
                    4. 忽略文本中的 `<|LOC_xxx|>`、`<fcel>` 等乱码。
                    5. 仅输出最终的文件名，不要任何标点符号，不要任何废话，总长度控制在30字以内。

                    【参考示例】

                    输入：...来宾市博物馆数字体验创新空间建设项目...同意支付第1期工程施工进度款...268317.39元...
                    输出：来宾市博物馆数字体验创新空间建设项目_第1期工程款支付证书

                    ===现在开始处理以下文本===
                    文本：{ocr_text}"""
                url = f"{self.base_url}/chat/completions"
                headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
                payload = {
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                    "max_tokens": 100
                }
                response = httpx.post(url, json=payload, headers=headers, timeout=config.REQUEST_TIMEOUT)
                response.raise_for_status()
                content = response.json()['choices'][0]['message']['content'].strip()
                # 清理文件名，移除可能的标点符号
                content = content.replace(':', '').replace('：', '').replace(',', '').replace('，', '').replace('.', '').replace('。', '').replace('?', '').replace('？', '').replace('!', '').replace('！', '').replace(';', '').replace('；', '').replace('"', '').replace('“', '').replace('”', '').replace("'", '').replace('‘', '').replace('’', '').replace('(', '').replace(')', '').replace('（', '').replace('）', '')
                # 限制文件名长度
                content = content[:30].strip()
                # 返回格式保持一致，title为文件名，date为空
                logger.info(f"LLM 提取成功 (重试 {retry+1}/{max_retries})")
                return {"title": content}
            except Exception as e:
                logger.error(f"LLM 提取失败 (重试 {retry+1}/{max_retries})：{e}")
                if retry < max_retries - 1:
                    import time
                    logger.info(f"等待 {retry_delay} 秒后重试...")
                    time.sleep(retry_delay)
                else:
                    return None