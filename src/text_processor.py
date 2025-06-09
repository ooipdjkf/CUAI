"""
文本处理模块：负责处理建筑规范文档中的文本内容
"""
import re
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class TextSection:
    """表示文档中的一个文本段落"""
    content: str
    section_number: Optional[str] = None
    level: int = 0
    metadata: Dict = None

class TextProcessor:
    def __init__(self):
        self.sections: List[TextSection] = []
        
    def process_text(self, text: str) -> List[TextSection]:
        """
        处理输入的文本，将其分割成有意义的段落
        
        Args:
            text: 输入的文本内容
            
        Returns:
            List[TextSection]: 处理后的文本段落列表
        """
        # 分割文本为段落
        paragraphs = text.split('\n\n')
        
        for para in paragraphs:
            if not para.strip():
                continue
                
            # 尝试识别段落编号
            section_number = self._extract_section_number(para)
            level = self._determine_level(section_number) if section_number else 0
            
            section = TextSection(
                content=para.strip(),
                section_number=section_number,
                level=level,
                metadata={}
            )
            self.sections.append(section)
            
        return self.sections
    
    def _extract_section_number(self, text: str) -> Optional[str]:
        """
        从文本中提取段落编号
        
        Args:
            text: 输入文本
            
        Returns:
            Optional[str]: 提取到的编号，如果没有则返回None
        """
        # 匹配常见的编号格式，如：1.2.3, 1-2-3, 1.2.3.4 等
        pattern = r'^(\d+(?:[.-]\d+)*)'
        match = re.match(pattern, text.strip())
        return match.group(1) if match else None
    
    def _determine_level(self, section_number: str) -> int:
        """
        根据编号确定层级
        
        Args:
            section_number: 段落编号
            
        Returns:
            int: 层级深度
        """
        if not section_number:
            return 0
        # 计算分隔符的数量来确定层级
        return len(re.findall(r'[.-]', section_number)) + 1
    
    def to_json(self) -> Dict:
        """
        将处理后的文本转换为JSON格式
        
        Returns:
            Dict: JSON格式的文本内容
        """
        return {
            "sections": [
                {
                    "content": section.content,
                    "section_number": section.section_number,
                    "level": section.level,
                    "metadata": section.metadata
                }
                for section in self.sections
            ]
        } 