import fitz  # PyMuPDF
import argparse

def extract_pdf_pages(input_path: str, output_path: str, pages: str):
    """
    从PDF文件中提取指定页面并保存为新PDF
    
    参数:
        input_path: 输入PDF文件路径
        output_path: 输出PDF文件路径
        pages: 要提取的页面范围，如"1,3,5"或"1-5"
    """
    try:
        # 打开输入PDF文件
        doc = fitz.open(input_path)
        
        # 创建新PDF文档
        new_doc = fitz.open()
        
        # 解析页面范围
        page_list = []
        for part in pages.split(','):
            if '-' in part:
                start, end = map(int, part.split('-'))
                page_list.extend(range(start-1, end))
            else:
                page_list.append(int(part)-1)
        
        # 提取并添加指定页面
        for page_num in page_list:
            if 0 <= page_num < doc.page_count:
                new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
            else:
                print(f"警告: 页面 {page_num+1} 超出范围，已跳过")
        
        # 保存新PDF
        new_doc.save(output_path)
        print(f"成功提取页面并保存为 {output_path}")
        
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        doc.close()
        new_doc.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='从PDF中提取指定页面并生成新PDF')
    parser.add_argument('input', help='输入PDF文件路径')
    parser.add_argument('output', help='输出PDF文件路径')
    parser.add_argument('pages', help='要提取的页面范围，如"1,3,5"或"1-5"')
    
    args = parser.parse_args()
    
    extract_pdf_pages(args.input, args.output, args.pages)