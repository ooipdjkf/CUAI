"""
表格处理模块：负责处理建筑规范文档中的表格内容
"""
import pandas as pd
from typing import Dict, List, Optional, Union
from dataclasses import dataclass

@dataclass
class TableCell:
    """表示表格中的一个单元格"""
    content: str
    row: int
    col: int
    rowspan: int = 1
    colspan: int = 1
    metadata: Dict = None

@dataclass
class Table:
    """表示一个完整的表格"""
    caption: Optional[str] = None
    table_number: Optional[str] = None
    cells: List[TableCell] = None
    metadata: Dict = None

class TableProcessor:
    def __init__(self):
        self.tables: List[Table] = []
        
    def process_table(self, table_data: Union[pd.DataFrame, List[List[str]]], 
                     caption: Optional[str] = None,
                     table_number: Optional[str] = None) -> Table:
        """
        处理表格数据
        
        Args:
            table_data: 表格数据，可以是pandas DataFrame或二维列表
            caption: 表格标题
            table_number: 表格编号
            
        Returns:
            Table: 处理后的表格对象
        """
        if isinstance(table_data, pd.DataFrame):
            df = table_data
        else:
            df = pd.DataFrame(table_data)
            
        cells = []
        for i in range(len(df)):
            for j in range(len(df.columns)):
                cell = TableCell(
                    content=str(df.iloc[i, j]),
                    row=i,
                    col=j,
                    metadata={}
                )
                cells.append(cell)
                
        table = Table(
            caption=caption,
            table_number=table_number,
            cells=cells,
            metadata={}
        )
        self.tables.append(table)
        return table
    
    def extract_table_from_text(self, text: str) -> Optional[Table]:
        """
        从文本中提取表格
        
        Args:
            text: 包含表格的文本
            
        Returns:
            Optional[Table]: 提取到的表格，如果没有则返回None
        """
        # TODO: 实现从文本中提取表格的逻辑
        pass
    
    def to_json(self) -> Dict:
        """
        将处理后的表格转换为JSON格式
        
        Returns:
            Dict: JSON格式的表格内容
        """
        return {
            "tables": [
                {
                    "caption": table.caption,
                    "table_number": table.table_number,
                    "cells": [
                        {
                            "content": cell.content,
                            "row": cell.row,
                            "col": cell.col,
                            "rowspan": cell.rowspan,
                            "colspan": cell.colspan,
                            "metadata": cell.metadata
                        }
                        for cell in table.cells
                    ],
                    "metadata": table.metadata
                }
                for table in self.tables
            ]
        }
    
    def to_markdown(self) -> str:
        """
        将表格转换为Markdown格式
        
        Returns:
            str: Markdown格式的表格
        """
        markdown_tables = []
        for table in self.tables:
            if table.caption:
                markdown_tables.append(f"**{table.caption}**\n")
            if table.table_number:
                markdown_tables.append(f"*Table {table.table_number}*\n")
                
            # 创建表格头部
            max_col = max(cell.col for cell in table.cells)
            header = "| " + " | ".join([f"Column {i+1}" for i in range(max_col + 1)]) + " |"
            separator = "| " + " | ".join(["---" for _ in range(max_col + 1)]) + " |"
            
            markdown_tables.extend([header, separator])
            
            # 添加表格内容
            current_row = 0
            row_content = []
            for cell in sorted(table.cells, key=lambda x: (x.row, x.col)):
                if cell.row != current_row:
                    markdown_tables.append("| " + " | ".join(row_content) + " |")
                    row_content = []
                    current_row = cell.row
                row_content.append(cell.content)
            
            if row_content:
                markdown_tables.append("| " + " | ".join(row_content) + " |")
            
            markdown_tables.append("\n")
            
        return "\n".join(markdown_tables) 