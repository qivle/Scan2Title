import fitz
from pathlib import Path
from typing import List
import logging

logger = logging.getLogger(__name__)

def pdf_to_images(pdf_path: Path, max_pages: int = 1, dpi: int = 72) -> List[bytes]:
    """
    将 PDF 文件转换为图片列表，只取顶部区域（通常包含标题）
    """
    images = []
    try:
        doc = fitz.open(pdf_path)
        for page_num in range(min(len(doc), max_pages)):
            page = doc[page_num]
            # 使用更低的 DPI
            zoom = dpi / 72.0
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            
            # 只取图片的顶部区域（通常标题在顶部）
            width, height = pix.width, pix.height
            crop_width = min(800, width)
            crop_height = min(400, height)  # 只取顶部 400 像素
            
            # 裁剪图片 - 使用正确的方法
            if crop_width < width or crop_height < height:
                # 创建一个新的 pixmap，只包含顶部区域
                # 方法 1：使用页面的矩形裁剪
                rect = fitz.Rect(0, 0, crop_width, crop_height)
                new_pix = page.get_pixmap(matrix=mat, clip=rect)
                img_data = new_pix.tobytes("png")
            else:
                img_data = pix.tobytes("png")
            
            images.append(img_data)
        doc.close()
        logger.info(f"Converted {len(images)} pages")
        return images
    except Exception as e:
        logger.error(f"PDF conversion failed: {e}")
        raise