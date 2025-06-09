"""
建筑规范文档处理器主模块
"""
from typing import Dict, List, Optional
from .text_processor import TextProcessor, TextSection
from .table_processor import TableProcessor, Table
from .formula_processor import FormulaProcessor, Formula
from .numbering_processor import NumberingProcessor, NumberingNode

class BuildingCodeProcessor:
    """建筑规范文档处理器主类"""
    
    def __init__(self):
        self.text_processor = TextProcessor()
        self.table_processor = TableProcessor()
        self.formula_processor = FormulaProcessor()
        self.numbering_processor = NumberingProcessor()
        
    def process_document(self, text: str) -> Dict:
        """
        处理整个文档
        
        Args:
            text: 文档文本内容
            
        Returns:
            Dict: 处理后的文档内容
        """
        # 处理编号系统
        numbering_nodes = self.numbering_processor.process_numbering(text)
        
        # 处理文本内容
        text_sections = self.text_processor.process_text(text)
        
        # 处理表格
        tables = self.table_processor.extract_table_from_text(text)
        
        # 处理公式
        formulas = self.formula_processor.extract_formulas_from_text(text)
        
        return {
            "numbering": self.numbering_processor.to_json(),
            "text": self.text_processor.to_json(),
            "tables": self.table_processor.to_json(),
            "formulas": self.formula_processor.to_json()
        }
    
    def to_markdown(self) -> str:
        """
        将处理后的文档转换为Markdown格式
        
        Returns:
            str: Markdown格式的文档
        """
        markdown_parts = []
        
        # 添加编号系统
        markdown_parts.append("# 文档结构\n")
        markdown_parts.append(self.numbering_processor.to_markdown())
        markdown_parts.append("\n")
        
        # 添加表格
        markdown_parts.append("# 表格\n")
        markdown_parts.append(self.table_processor.to_markdown())
        markdown_parts.append("\n")
        
        # 添加公式
        markdown_parts.append("# 公式\n")
        for formula in self.formula_processor.formulas:
            markdown_parts.append(f"## 公式 {formula.formula_number}\n")
            markdown_parts.append(f"```latex\n{formula.latex}\n```\n")
            if formula.description:
                markdown_parts.append(f"{formula.description}\n")
            markdown_parts.append("\n")
            
        return "\n".join(markdown_parts)
    
    def to_json(self) -> Dict:
        """
        将处理后的文档转换为JSON格式
        
        Returns:
            Dict: JSON格式的文档内容
        """
        return {
            "numbering": self.numbering_processor.to_json(),
            "text": self.text_processor.to_json(),
            "tables": self.table_processor.to_json(),
            "formulas": self.formula_processor.to_json()
        } 