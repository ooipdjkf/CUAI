import json
import requests
from pathlib import Path
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BuildingCodeQA:
    """建筑规范问答系统"""
    
    def __init__(self, api_url: str = "http://127.0.0.1:1234"):
        self.api_url = f"{api_url}/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer lm-studio"
        }
        self.load_documents()
        
    def load_documents(self):
        """加载文档"""
        self.documents = {}
        data_dir = Path("processed_data")
        
        # 首先加载示例文件
        example_path = data_dir / "example.json"
        if example_path.exists():
            with open(example_path, 'r', encoding='utf-8') as f:
                self.documents['example'] = json.load(f)
                
        # 加载DBSE-A文件
        dbse_files = list(data_dir.glob("DBSE-A*.json"))
        if dbse_files:
            latest_dbse = max(dbse_files, key=lambda x: x.stat().st_mtime)
            if not latest_dbse.name.endswith('_stats.json'):
                with open(latest_dbse, 'r', encoding='utf-8') as f:
                    self.documents['DBSE-A'] = json.load(f)
                    
        # 加载RSCIEI文件
        rsciei_files = list(data_dir.glob("RSCIEI*.json"))
        if rsciei_files:
            latest_rsciei = max(rsciei_files, key=lambda x: x.stat().st_mtime)
            if not latest_rsciei.name.endswith('_stats.json'):
                with open(latest_rsciei, 'r', encoding='utf-8') as f:
                    self.documents['RSCIEI'] = json.load(f)
                    
        logger.info(f"已加载规范文档: {', '.join(self.documents.keys())}")
        
    def get_document_info(self):
        """获取文档信息"""
        info = []
        for doc_name, doc_data in self.documents.items():
            if isinstance(doc_data, dict) and 'data' in doc_data:
                sections = doc_data['data'].get('sections', {})
                section_titles = []
                for section_id, section in sections.items():
                    title = section.get('data', {}).get('title_es', '')
                    if title:
                        section_titles.append(f"{section_id}: {title}")
                info.append(f"\n{doc_name} 包含以下章节：\n" + "\n".join(section_titles))
        return "\n".join(info)
        
    def query(self, doc_name: str, section_id: str, question: str) -> str:
        """查询特定章节"""
        try:
            # 获取章节数据
            doc_data = self.documents.get(doc_name, {})
            if isinstance(doc_data, dict) and 'data' in doc_data:
                doc_data = doc_data['data']
                
            section = doc_data.get('sections', {}).get(section_id, {}).get('data', {})
            if not section:
                return "未找到指定章节。"
                
            # 准备上下文
            context_parts = [
                f"章节：{section.get('title_es', '')}",
                f"内容：{section.get('content_es', '')}"
            ]
            
            # 添加要求
            requirements = section.get('requirements', [])
            if requirements:
                context_parts.append("\n要求：")
                for req in requirements:
                    context_parts.append(f"- {req.get('text_es', '')}")
                    
            context = "\n".join(context_parts)
            
            # 准备提示
            messages = [
                {"role": "system", "content": "你是一个专门解答西班牙建筑规范问题的专家。请根据提供的规范内容，准确回答问题。如果找不到相关内容，请明确说明。"},
                {"role": "user", "content": f"相关规范内容：\n\n{context}\n\n问题：{question}"}
            ]
            
            # 发送请求
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={
                    "model": "deepseek-r1-distill-qwen-7b",
                    "messages": messages,
                    "temperature": 0.7
                }
            )
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
            
        except Exception as e:
            logger.error(f"查询时出错: {str(e)}")
            return f"发生错误: {str(e)}"

def main():
    print("\n=== 建筑规范问答系统 ===")
    print("(输入 'quit' 退出)")
    
    # 初始化系统
    qa_system = BuildingCodeQA()
    
    # 显示可用文档信息
    print("\n可用的规范文档和章节：")
    print(qa_system.get_document_info())
    
    while True:
        print("\n请选择要查询的文档和章节：")
        doc_name = input("文档名称 (例如 DBSE-A): ").strip()
        if doc_name.lower() in ['quit', 'exit', 'q']:
            break
            
        section_id = input("章节编号: ").strip()
        if section_id.lower() in ['quit', 'exit', 'q']:
            break
            
        question = input("请输入您的问题: ").strip()
        if question.lower() in ['quit', 'exit', 'q']:
            break
            
        print("\n正在查询...")
        response = qa_system.query(doc_name, section_id, question)
        
        print("\n回答：")
        print("-" * 50)
        print(response)
        print("-" * 50)

if __name__ == "__main__":
    main() 