import json
import requests
from pathlib import Path
import logging
from typing import List, Dict
import jieba
from collections import Counter

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentSearcher:
    """内容搜索器"""
    
    def __init__(self, data_dir: str = "processed_data"):
        self.data_dir = Path(data_dir)
        self.documents = {}
        self.load_documents()
        
    def load_documents(self):
        """加载所有文档"""
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
                
    def extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 使用结巴分词提取关键词
        words = jieba.cut(text)
        return [w for w in words if len(w) > 1]  # 只保留长度大于1的词
        
    def calculate_relevance(self, keywords: List[str], content: str) -> float:
        """计算相关性分数"""
        content_words = self.extract_keywords(content.lower())
        word_count = Counter(content_words)
        
        score = 0
        for keyword in keywords:
            score += word_count[keyword.lower()]
        return score
        
    def find_relevant_sections(self, question: str, top_k: int = 2) -> List[Dict]:
        """查找与问题最相关的章节"""
        keywords = self.extract_keywords(question)
        relevant_sections = []
        
        for doc_name, doc_data in self.documents.items():
            sections = doc_data.get('sections', {})
            for section_id, section in sections.items():
                section_data = section.get('data', {})
                
                # 合并标题和内容用于相关性计算
                content = f"{section_data.get('title_es', '')} {section_data.get('content_es', '')}"
                
                # 计算相关性分数
                score = self.calculate_relevance(keywords, content)
                
                if score > 0:
                    relevant_sections.append({
                        'doc_name': doc_name,
                        'section_id': section_id,
                        'data': section_data,
                        'score': score
                    })
                    
        # 按相关性分数排序并返回top_k个结果
        relevant_sections.sort(key=lambda x: x['score'], reverse=True)
        return relevant_sections[:top_k]

def query_model(question: str, context: str = "") -> str:
    """向模型发送请求"""
    url = "http://127.0.0.1:1234/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer lm-studio"
    }
    
    # 准备提示
    messages = [
        {"role": "system", "content": "你是一个专门解答西班牙建筑规范问题的专家。请根据提供的规范内容，准确回答问题。如果找不到相关内容，请明确说明。"},
        {"role": "user", "content": f"相关规范内容：\n\n{context}\n\n问题：{question}" if context else question}
    ]
    
    try:
        response = requests.post(
            url,
            headers=headers,
            json={
                "model": "deepseek-r1-distill-qwen-7b",
                "messages": messages,
                "temperature": 0.7
            }
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"发生错误: {str(e)}"

def format_section_context(section_data: Dict) -> str:
    """格式化章节上下文"""
    context_parts = [
        f"章节：{section_data.get('title_es', '')}",
        f"内容：{section_data.get('content_es', '')}"
    ]
    
    # 添加要求
    requirements = section_data.get('requirements', [])
    if requirements:
        context_parts.append("\n要求：")
        for req in requirements:
            context_parts.append(f"- {req.get('text_es', '')}")
            
    return "\n".join(context_parts)

def main():
    print("\n=== 建筑规范智能问答系统 ===")
    print("(输入 'quit' 退出)")
    
    # 初始化搜索器
    searcher = ContentSearcher()
    print(f"\n已加载 {len(searcher.documents)} 个规范文档")
    
    while True:
        # 获取用户问题
        question = input("\n请输入您的问题: ").strip()
        if question.lower() in ['quit', 'exit', 'q']:
            break
            
        if not question:
            continue
            
        # 搜索相关章节
        print("\n正在搜索相关内容...")
        relevant_sections = searcher.find_relevant_sections(question)
        
        if not relevant_sections:
            print("未找到相关内容。")
            continue
            
        # 整合相关章节的内容
        contexts = []
        print("\n找到以下相关章节：")
        for idx, section in enumerate(relevant_sections, 1):
            print(f"{idx}. 来自文档 {section['doc_name']}: {section['data'].get('title_es', '')}")
            contexts.append(format_section_context(section['data']))
            
        # 合并上下文并查询模型
        context = "\n\n---\n\n".join(contexts)
        print("\n正在思考...")
        response = query_model(question, context)
        
        print("\n回答：")
        print("-" * 50)
        print(response)
        print("-" * 50)

if __name__ == "__main__":
    main() 