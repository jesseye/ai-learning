import fitz  # PyMuPDF
import re
import os
from typing import List, Dict

def pdf_to_markdown(pdf_path: str) -> str:
    """
    将PDF文件转换为Markdown格式
    
    参数:
        pdf_path: PDF文件路径
        
    返回:
        Markdown格式的字符串
    """
    doc = fitz.open(pdf_path)
    markdown_content = ""
    
    for page in doc:
        # 提取文本和格式信息
        text_blocks = page.get_text("dict")["blocks"]
        
        # 分析字体大小分布确定标题级别
        font_sizes = []
        for block in text_blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        font_sizes.append(span["size"])
        
        if font_sizes:
            max_size = max(font_sizes)
            min_size = min(font_sizes)
            size_ranges = {
                1: max_size * 0.9,  # h1
                2: max_size * 0.8,   # h2
                3: max_size * 0.7,   # h3
                4: max_size * 0.6    # h4
            }
        
        # 添加页面分隔符
        markdown_content += f"\n\n--- Page {page.number + 1} ---\n\n"
        
        # 提取并保存图片
        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            
            # 创建图片目录
            image_dir = os.path.join(os.path.dirname(args.output), "images")
            os.makedirs(image_dir, exist_ok=True)
            
            # 保存图片
            image_path = os.path.join(image_dir, f"page_{page.number+1}_img_{img_index}.{image_ext}")
            with open(image_path, "wb") as f:
                f.write(image_bytes)
            
            # 添加Markdown图片引用
            rel_image_path = os.path.join("images", f"page_{page.number+1}_img_{img_index}.{image_ext}")
            markdown_content += f"![Image]({rel_image_path})\n\n"
        
        # 格式化文本块
        for block in text_blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"]
                        size = span["size"]
                        
                        # 确定标题级别
                        heading_level = None
                        for level, threshold in size_ranges.items():
                            if size >= threshold:
                                heading_level = level
                                break
                        
                        if heading_level:
                            markdown_content += f"{'#' * heading_level} {text}\n\n"
                        else:
                            markdown_content += f"{text} "
                    markdown_content += "\n"
    
    return markdown_content

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='将PDF转换为Markdown格式')
    parser.add_argument('pdf_file', help='输入的PDF文件路径')
    parser.add_argument('--output', '-o', help='输出的Markdown文件路径', default='output.md')
    
    args = parser.parse_args()
    
    markdown_text = pdf_to_markdown(args.pdf_file)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(markdown_text)
    
    print(f"成功将 {args.pdf_file} 转换为Markdown格式，保存为 {args.output}")