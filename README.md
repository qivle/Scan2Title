# Scan2Title - PDF OCR 识别与自动重命名工具

一个自动化工具，用于批量处理 PDF 扫描件，通过 OCR 识别文档信息并智能重命名文件。

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置 API Key
编辑 `config.py` 文件，填入你的 SiliconFlow API Key：
```python
SILICONFLOW_API_KEY = "your-api-key-here"  # 填入你的 API Key
```

### 3. 创建文件夹结构
在项目根目录下创建两个文件夹：
```
Scan2Title/
├── input/      # 放入待处理的 PDF 文件
├── output/     # 处理后的文件会输出到这里
└── ...
```

**重要：** 程序不会自动创建 `input` 文件夹，需要手动创建。

### 4. 放入 PDF 文件
将需要处理的 PDF 扫描件放入 `input` 文件夹。

### 5. 运行程序
```bash
python main.py
```

### 6. 查看结果
- 处理后的文件会在 `output` 文件夹中，以识别的标题和日期命名
- 详细的处理日志会保存在 `output/process_log_*.txt`

## 核心功能
- 📄 批量处理 PDF 扫描件，自动识别文档标题
- 🔍 使用云端 PaddleOCR-VL-1.5 进行高精度文字识别
- 🤖 集成 Qwen2.5-7B-Instruct 模型提取关键信息
- ⚡ 多线程并发处理，提高批量处理速度
- 📊 详细的处理日志和文件命名记录
- 🔄 网络超时自动重试机制，提高稳定性

## 技术栈
- Python 3.13+
- PyMuPDF (fitz) - PDF 处理
- httpx - API 调用
- concurrent.futures - 多线程处理
- SiliconFlow API - 云端 OCR 和 LLM 服务

## 使用场景
- 批量整理扫描文档
- 自动归档合同、函件等文件
- 构建文档管理系统的预处理工具

## 特点
- 支持中文文档识别
- 智能生成简洁明了的文件名
- 可配置的 DPI 设置，平衡识别质量和处理速度
- 完善的错误处理和日志记录

## 配置说明

在 `config.py` 中可以调整以下参数：
- `MAX_PAGES_TO_SCAN`: 每个 PDF 扫描的最大页数（默认：1）
- `IMAGE_DPI`: PDF 转图片的 DPI（默认：150）
- `REQUEST_TIMEOUT`: API 请求超时时间（默认：60 秒）

## 注意事项
1. 确保 API Key 有效且有足够的额度
2. `input` 文件夹需要手动创建
3. 只处理 `.pdf` 格式的文件
4. 处理失败的文件信息会记录在日志中
