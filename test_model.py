import json
import requests
from pathlib import Path
import logging
from typing import Dict, List, Optional

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LocalLLMClient:
    """本地LLM模型客户端"""
    
    def __init__(self, api_url: str = "http://127.0.0.1:1234"):
        self.api_url = f"{api_url}/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer lm-studio"
        }
        
    def query(self, question: str, context: str = "") -> str:
        """
        向模型发送问题
        Args:
            question: 问题
            context: 相关上下文
        Returns:
            模型的回答
        """
        try:
            # 准备提示
            system_prompt = "你是一个专门解答西班牙建筑规范问题的专家。请根据提供的规范内容，准确回答问题。"
            if context:
                user_prompt = f"相关规范内容：\n\n{context}\n\n问题：{question}"
            else:
                user_prompt = question
                
            # 准备请求数据
            data = {
                "model": "deepseek-r1-distill-qwen-7b",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.7
            }
            
            # 发送请求
            response = requests.post(self.api_url, headers=self.headers, json=data)
            response.raise_for_status()
            
            # 解析响应
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except Exception as e:
            logger.error(f"查询模型时出错: {str(e)}")
            return f"发生错误: {str(e)}"

class BuildingCodeData:
    """建筑规范数据管理器"""
    
    def __init__(self, data_dir: str = "processed_data"):
        self.data_dir = Path(data_dir)
        self.documents = {}
        self.load_all_documents()
        
    def load_all_documents(self):
        """加载所有规范文档"""
        json_files = list(self.data_dir.glob("*.json"))
        json_files = [f for f in json_files if not f.name.endswith("_stats.json")]
        
        for file_path in json_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                doc_name = file_path.stem
                if isinstance(data, dict) and 'data' in data:
                    self.documents[doc_name] = data['data']
                else:
                    self.documents[doc_name] = data
                logger.info(f"已加载文档: {doc_name}")
            except Exception as e:
                logger.error(f"加载文档 {file_path} 时出错: {str(e)}")
                
    def get_document_names(self) -> List[str]:
        """获取所有文档名称"""
        return list(self.documents.keys())
        
    def get_section_titles(self, doc_name: str) -> Dict[str, str]:
        """获取指定文档的所有章节标题"""
        if doc_name not in self.documents:
            return {}
            
        titles = {}
        sections = self.documents[doc_name].get('sections', {})
        for section_id, section in sections.items():
            title = section.get('data', {}).get('title_es', '')
            if title:
                titles[section_id] = title
        return titles
        
    def get_section_data(self, doc_name: str, section_id: str) -> Optional[Dict]:
        """获取指定章节的数据"""
        if doc_name not in self.documents:
            return None
            
        sections = self.documents[doc_name].get('sections', {})
        return sections.get(section_id, {}).get('data')

def format_section_context(section_data):
    """格式化章节上下文"""
    if not section_data:
        return ""
        
    context = []
    
    # 添加标题和内容
    title = section_data.get('title_es', '')
    content = section_data.get('content_es', '')
    context.extend([
        f"标题：{title}",
        f"内容：{content}"
    ])
    
    # 添加要求
    requirements = section_data.get('requirements', [])
    if requirements:
        context.append("\n要求：")
        for req in requirements:
            context.append(f"- {req.get('text_es', '')}")
            
    # 添加公式
    formulas = section_data.get('formulas', {})
    if formulas:
        context.append("\n公式：")
        for formula_id, formula in formulas.items():
            formula_data = formula.get('data', {})
            context.extend([
                f"公式 {formula_id}：{formula_data.get('expression', '')}",
                f"说明：{formula_data.get('context_es', '')}"
            ])
            
            # 添加变量说明
            variables = formula_data.get('variables', {})
            if variables:
                context.append("变量：")
                for var, desc in variables.items():
                    context.append(f"- {var}: {desc}")
                    
    return "\n".join(context)

def interactive_test():
    """交互式测试"""
    # 初始化
    client = LocalLLMClient()
    data_manager = BuildingCodeData()
    
    # 显示可用文档
    print("\n可用的规范文档：")
    for idx, doc_name in enumerate(data_manager.get_document_names(), 1):
        print(f"{idx}. {doc_name}")
        
    # 选择文档
    doc_idx = int(input("\n请选择要查询的文档 (输入编号): ")) - 1
    doc_name = data_manager.get_document_names()[doc_idx]
    
    # 显示章节
    print(f"\n{doc_name} 的章节：")
    titles = data_manager.get_section_titles(doc_name)
    for section_id, title in titles.items():
        print(f"{section_id}. {title}")
        
    # 选择章节
    section_id = input("\n请选择要查询的章节编号: ")
    
    # 获取章节数据
    section_data = data_manager.get_section_data(doc_name, section_id)
    if not section_data:
        print("未找到章节数据")
        return
        
    # 格式化上下文
    context = format_section_context(section_data)
    
    # 获取用户问题
    question = input("\n请输入您的问题: ")
    
    # 发送查询
    logger.info("发送问题到模型...")
    logger.info(f"问题: {question}")
    logger.info(f"\n上下文:\n{context}\n")
    
    response = client.query(question, context)
    logger.info("\n模型回答:")
    print(response)

if __name__ == "__main__":
    interactive_test() 