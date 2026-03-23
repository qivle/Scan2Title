import shutil
from pathlib import Path
from typing import Optional
import logging
from datetime import datetime
import config

logger = logging.getLogger(__name__)


def sanitize_filename(filename: str) -> str:
    """
    清理文件名，移除非法字符
    
    Args:
        filename: 原始文件名
        
    Returns:
        清理后的文件名
    """
    illegal_chars = '<>:"/\\|？*'
    for char in illegal_chars:
        filename = filename.replace(char, "_")
    return filename.strip()


def generate_filename(title: Optional[str], date: Optional[str]) -> str:
    """
    生成文件名
    
    Args:
        title: 文档标题
        date: 日期
        
    Returns:
        生成的文件名
    """
    if not title:
        title = "未命名文档"
    
    if date:
        filename = f"{sanitize_filename(title)}_{date}.pdf"
    else:
        filename = f"{sanitize_filename(title)}.pdf"
    
    return filename


def copy_and_rename(src: Path, dest_dir: Path, title: Optional[str], date: Optional[str]) -> Optional[Path]:
    """
    复制并重命名文件
    
    Args:
        src: 源文件路径
        dest_dir: 目标目录
        title: 文档标题
        date: 日期
        
    Returns:
        目标文件路径，失败返回 None
    """
    try:
        filename = generate_filename(title, date)
        dest_path = dest_dir / filename
        
        # 处理重名
        if dest_path.exists():
            timestamp = datetime.now().strftime("%H%M%S")
            stem = dest_path.stem
            suffix = dest_path.suffix
            dest_path = dest_dir / f"{stem}_{timestamp}{suffix}"
        
        shutil.copy2(src, dest_path)
        logger.info(f"已复制文件：{dest_path.name}")
        return dest_path
        
    except Exception as e:
        logger.error(f"文件复制失败：{e}")
        return None
