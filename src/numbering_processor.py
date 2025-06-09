"""
编号系统处理模块：负责处理建筑规范文档中的编号系统
"""
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class NumberingNode:
    """表示编号系统中的一个节点"""
    number: str
    level: int
    title: str
    parent: Optional['NumberingNode'] = None
    children: List['NumberingNode'] = None
    metadata: Dict = None

class NumberingProcessor:
    def __init__(self):
        self.root_nodes: List[NumberingNode] = []
        self._number_pattern = r'^(\d+(?:[.-]\d+)*)'
        
    def process_numbering(self, text: str) -> List[NumberingNode]:
        """
        处理文本中的编号系统
        
        Args:
            text: 包含编号的文本
            
        Returns:
            List[NumberingNode]: 处理后的编号节点列表
        """
        lines = text.split('\n')
        current_path: List[NumberingNode] = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 尝试匹配编号
            match = re.match(self._number_pattern, line)
            if not match:
                continue
                
            number = match.group(1)
            level = self._get_level(number)
            title = line[match.end():].strip()
            
            # 创建新节点
            node = NumberingNode(
                number=number,
                level=level,
                title=title,
                children=[],
                metadata={}
            )
            
            # 处理节点层级关系
            self._handle_node_hierarchy(node, current_path)
            
        return self.root_nodes
    
    def _get_level(self, number: str) -> int:
        """
        根据编号确定层级
        
        Args:
            number: 编号字符串
            
        Returns:
            int: 层级深度
        """
        return len(re.findall(r'[.-]', number)) + 1
    
    def _handle_node_hierarchy(self, node: NumberingNode, 
                             current_path: List[NumberingNode]) -> None:
        """
        处理节点的层级关系
        
        Args:
            node: 当前节点
            current_path: 当前路径
        """
        # 如果当前路径为空，将节点添加为根节点
        if not current_path:
            self.root_nodes.append(node)
            current_path.append(node)
            return
            
        # 找到合适的父节点
        while current_path and current_path[-1].level >= node.level:
            current_path.pop()
            
        if current_path:
            parent = current_path[-1]
            node.parent = parent
            parent.children.append(node)
        else:
            self.root_nodes.append(node)
            
        current_path.append(node)
    
    def get_node_by_number(self, number: str) -> Optional[NumberingNode]:
        """
        根据编号查找节点
        
        Args:
            number: 要查找的编号
            
        Returns:
            Optional[NumberingNode]: 找到的节点，如果没有则返回None
        """
        def search_node(node: NumberingNode) -> Optional[NumberingNode]:
            if node.number == number:
                return node
            for child in node.children:
                result = search_node(child)
                if result:
                    return result
            return None
            
        for root in self.root_nodes:
            result = search_node(root)
            if result:
                return result
        return None
    
    def get_full_path(self, node: NumberingNode) -> List[NumberingNode]:
        """
        获取节点的完整路径
        
        Args:
            node: 目标节点
            
        Returns:
            List[NumberingNode]: 从根节点到目标节点的路径
        """
        path = []
        current = node
        while current:
            path.append(current)
            current = current.parent
        return list(reversed(path))
    
    def to_json(self) -> Dict:
        """
        将编号系统转换为JSON格式
        
        Returns:
            Dict: JSON格式的编号系统
        """
        def node_to_dict(node: NumberingNode) -> Dict:
            return {
                "number": node.number,
                "level": node.level,
                "title": node.title,
                "children": [node_to_dict(child) for child in node.children],
                "metadata": node.metadata
            }
            
        return {
            "nodes": [node_to_dict(root) for root in self.root_nodes]
        }
    
    def to_markdown(self) -> str:
        """
        将编号系统转换为Markdown格式
        
        Returns:
            str: Markdown格式的编号系统
        """
        def node_to_markdown(node: NumberingNode, level: int = 0) -> str:
            indent = "  " * level
            result = [f"{indent}- {node.number} {node.title}"]
            for child in node.children:
                result.append(node_to_markdown(child, level + 1))
            return "\n".join(result)
            
        return "\n".join(node_to_markdown(root) for root in self.root_nodes) 