import re
from typing import List, Dict, Tuple
import markdown
from bs4 import BeautifulSoup
import requests
from PIL import Image
import pytesseract
import pdfplumber
import numpy as np
from sentence_transformers import SentenceTransformer

class MarkdownEmbedder:
    def __init__(self):
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        
    def parse_markdown(self, md_content: str) -> Dict:
        """解析Markdown内容，提取标题层级和图片链接"""
        html = markdown.markdown(md_content)
        soup = BeautifulSoup(html, 'html.parser')
        
        # 提取标题
        headings = {}
        for i in range(1, 5):
            headings[f'h{i}'] = [h.get_text() for h in soup.find_all(f'h{i}')]
        
        # 提取图片链接
        images = [img['src'] for img in soup.find_all('img') if 'src' in img.attrs]
        
        return {
            'headings': headings,
            'images': images,
            'paragraphs': [p.get_text() for p in soup.find_all('p')]
        }
    
    def extract_text_from_image(self, image_url: str) -> str:
        """使用OCR从图片中提取文字"""
        try:
            response = requests.get(image_url, stream=True)
            img = Image.open(response.raw)
            return pytesseract.image_to_string(img)
        except Exception as e:
            print(f"Error processing image {image_url}: {str(e)}")
            return ""
    
    def generate_embeddings(self, text: str) -> List[float]:
        """生成文本嵌入向量"""
        return self.model.encode(text).tolist()
    
    def semantic_chunking(self, text: str, threshold: float = 0.85) -> List[str]:
        """
        基于语义相似度对文本进行分块
        :param text: 输入文本
        :param threshold: 相似度阈值，默认为0.85
        :return: 分块后的文本列表
        """
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s', text)
        if len(sentences) <= 1:
            return [text]
            
        embeddings = self.model.encode(sentences)
        chunks = []
        current_chunk = sentences[0]
        
        for i in range(1, len(sentences)):
            similarity = cosine_similarity(
                embeddings[i-1].reshape(1, -1),
                embeddings[i].reshape(1, -1)
            )[0][0]
            
            if similarity >= threshold:
                current_chunk += " " + sentences[i]
            else:
                chunks.append(current_chunk)
                current_chunk = sentences[i]
        
        chunks.append(current_chunk)
        return chunks
        
    def extract_tables_from_pdf(self, pdf_path: str) -> List[Dict[str, str]]:
        """从PDF中提取表格数据"""
        tables = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    for table in page.extract_tables():
                        # 将表格转换为结构化数据
                        table_data = []
                        for row in table:
                            table_data.append(" | ".join([str(cell) if cell is not None else "" for cell in row]))
                        tables.append({
                            'text': "\n".join(table_data),
                            'page': page.page_number
                        })
        except Exception as e:
            print(f"Error processing PDF {pdf_path}: {str(e)}")
        return tables
        
    def embed_markdown(self, md_content: str, pdf_path: str = None) -> Dict:
        """处理Markdown文档并生成嵌入向量，可选处理PDF中的表格"""
        parsed = self.parse_markdown(md_content)
        
        # 处理标题和段落
        text_embeddings = {}
        for level, headings in parsed['headings'].items():
            for heading in headings:
                text_embeddings[f"heading_{level}_{heading}"] = self.generate_embeddings(heading)
        
        # 对段落进行语义分块
        chunk_embeddings = {}
        for i, paragraph in enumerate(parsed['paragraphs']):
            chunks = self.semantic_chunking(paragraph)
            for j, chunk in enumerate(chunks):
                chunk_embeddings[f"paragraph_{i}_chunk_{j}"] = self.generate_embeddings(chunk)
        
        # 处理图片
        image_embeddings = {}
        for img_url in parsed['images']:
            img_text = self.extract_text_from_image(img_url)
            if img_text:
                image_embeddings[img_url] = {
                    'text': img_text,
                    'embedding': self.generate_embeddings(img_text)
                }
                
        # 处理PDF表格
        table_embeddings = {}
        if pdf_path:
            tables = self.extract_tables_from_pdf(pdf_path)
            for i, table in enumerate(tables):
                table_embeddings[f"table_{i}_page_{table['page']}"] = {
                    'text': table['text'],
                    'embedding': self.generate_embeddings(table['text'])
                }
        
        return {
            'text_embeddings': {**text_embeddings, **chunk_embeddings},
            'image_embeddings': image_embeddings,
            'table_embeddings': table_embeddings
        }

if __name__ == "__main__":
    # 示例用法
    with open('example.md', 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    embedder = MarkdownEmbedder()
    embeddings = embedder.embed_markdown(md_content)
    print(embeddings)