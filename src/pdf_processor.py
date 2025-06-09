"""
PDF处理模块：负责处理建筑规范PDF文档
"""
import os
import pandas as pd
import PyPDF2
import tabula
import json
import re
from typing import Dict, List, Any, Optional
from pathlib import Path
from PyPDF2 import PdfReader
from .text_processor import TextProcessor
from .table_processor import TableProcessor
from .formula_processor import FormulaProcessor
from .numbering_processor import NumberingProcessor

# 设置 Java 路径
os.environ['JAVA_HOME'] = r'C:\Program Files\Java\jdk-24'
os.environ['PATH'] = r'C:\Program Files\Java\jdk-24\bin;C:\Program Files\Java\jdk-24\bin\server;' + os.environ['PATH']

class PDFProcessor:
    def __init__(self):
        self.text_processor = TextProcessor()
        self.table_processor = TableProcessor()
        self.formula_processor = FormulaProcessor()
        self.numbering_processor = NumberingProcessor()
        
    def process_pdf(self, pdf_path: str) -> Dict:
        """
        处理PDF文件
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            Dict: 处理后的文档内容
        """
        print(f"正在处理文件: {os.path.basename(pdf_path)}")
        
        # 1. 提取文本
        print("正在提取文本...")
        text_content = self._extract_text(pdf_path)
        
        # 2. 提取表格
        print("正在提取表格...")
        tables = self._extract_tables(pdf_path)
        
        # 3. 处理文本内容
        print("正在处理文本内容...")
        text_sections = self.text_processor.process_text(text_content)
        
        # 4. 处理编号系统
        print("正在处理编号系统...")
        numbering_nodes = self.numbering_processor.process_numbering(text_content)
        
        # 5. 处理公式
        print("正在处理公式...")
        formulas = self.formula_processor.extract_formulas_from_text(text_content)
        
        # 6. 处理表格
        print("正在处理表格...")
        for table in tables:
            self.table_processor.process_table(table)
            
        return {
            "numbering": self.numbering_processor.to_json(),
            "text": self.text_processor.to_json(),
            "tables": self.table_processor.to_json(),
            "formulas": self.formula_processor.to_json()
        }
    
    def _extract_text(self, pdf_path: str) -> str:
        """提取PDF中的文本内容"""
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    
    def _extract_tables(self, pdf_path: str) -> List[pd.DataFrame]:
        """提取PDF中的表格"""
        return tabula.read_pdf(pdf_path, pages='all')
    
    def save_to_json(self, data: Dict, output_path: str) -> None:
        """保存处理结果到JSON文件"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
    def save_to_markdown(self, data: Dict, output_path: str) -> None:
        """保存处理结果到Markdown文件"""
        markdown_content = []
        
        # 添加编号系统
        markdown_content.append("# 文档结构\n")
        markdown_content.append(self.numbering_processor.to_markdown())
        markdown_content.append("\n")
        
        # 添加表格
        markdown_content.append("# 表格\n")
        markdown_content.append(self.table_processor.to_markdown())
        markdown_content.append("\n")
        
        # 添加公式
        markdown_content.append("# 公式\n")
        for formula in self.formula_processor.formulas:
            markdown_content.append(f"## 公式 {formula.formula_number}\n")
            markdown_content.append(f"```latex\n{formula.latex}\n```\n")
            if formula.description:
                markdown_content.append(f"{formula.description}\n")
            markdown_content.append("\n")
            
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(markdown_content)) 