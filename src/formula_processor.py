"""
公式处理模块：负责处理建筑规范文档中的数学公式
"""
import re
from typing import Dict, List, Optional
from dataclasses import dataclass
import sympy as sp
from latex2mathml.converter import convert as latex_to_mathml

@dataclass
class Formula:
    """表示一个数学公式"""
    latex: str
    formula_number: Optional[str] = None
    description: Optional[str] = None
    variables: Dict[str, str] = None
    metadata: Dict = None

class FormulaProcessor:
    def __init__(self):
        self.formulas: List[Formula] = []
        
    def process_formula(self, latex: str, 
                       formula_number: Optional[str] = None,
                       description: Optional[str] = None) -> Formula:
        """
        处理LaTeX格式的数学公式
        
        Args:
            latex: LaTeX格式的公式
            formula_number: 公式编号
            description: 公式描述
            
        Returns:
            Formula: 处理后的公式对象
        """
        # 提取公式中的变量
        variables = self._extract_variables(latex)
        
        formula = Formula(
            latex=latex,
            formula_number=formula_number,
            description=description,
            variables=variables,
            metadata={}
        )
        self.formulas.append(formula)
        return formula
    
    def _extract_variables(self, latex: str) -> Dict[str, str]:
        """
        从LaTeX公式中提取变量
        
        Args:
            latex: LaTeX格式的公式
            
        Returns:
            Dict[str, str]: 变量名到变量描述的映射
        """
        # 使用sympy解析LaTeX公式
        try:
            expr = sp.parse_latex(latex)
            variables = {}
            for symbol in expr.free_symbols:
                variables[str(symbol)] = f"Variable {symbol}"
            return variables
        except:
            return {}
    
    def to_mathml(self, formula: Formula) -> str:
        """
        将LaTeX公式转换为MathML格式
        
        Args:
            formula: 公式对象
            
        Returns:
            str: MathML格式的公式
        """
        try:
            return latex_to_mathml(formula.latex)
        except:
            return ""
    
    def to_json(self) -> Dict:
        """
        将处理后的公式转换为JSON格式
        
        Returns:
            Dict: JSON格式的公式内容
        """
        return {
            "formulas": [
                {
                    "latex": formula.latex,
                    "formula_number": formula.formula_number,
                    "description": formula.description,
                    "variables": formula.variables,
                    "metadata": formula.metadata
                }
                for formula in self.formulas
            ]
        }
    
    def extract_formulas_from_text(self, text: str) -> List[Formula]:
        """
        从文本中提取公式
        
        Args:
            text: 包含公式的文本
            
        Returns:
            List[Formula]: 提取到的公式列表
        """
        # 匹配常见的公式格式，如 $...$, $$...$$, \[...\], \(...\)
        patterns = [
            r'\$(.*?)\$',           # 行内公式
            r'\$\$(.*?)\$\$',       # 独立公式
            r'\\\[(.*?)\\\]',       # 独立公式
            r'\\\((.*?)\\\)'        # 行内公式
        ]
        
        formulas = []
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.DOTALL)
            for match in matches:
                latex = match.group(1).strip()
                # 尝试提取公式编号
                formula_number = self._extract_formula_number(text, match.start())
                formula = self.process_formula(latex, formula_number)
                formulas.append(formula)
                
        return formulas
    
    def _extract_formula_number(self, text: str, formula_pos: int) -> Optional[str]:
        """
        从文本中提取公式编号
        
        Args:
            text: 包含公式的文本
            formula_pos: 公式在文本中的位置
            
        Returns:
            Optional[str]: 提取到的公式编号
        """
        # 在公式后查找编号，如 (1), (1.1), (1-1) 等
        pattern = r'\((\d+(?:[.-]\d+)*)\)'
        match = re.search(pattern, text[formula_pos:])
        return match.group(1) if match else None 