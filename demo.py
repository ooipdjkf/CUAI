import json
import requests
from pathlib import Path
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def query_model(question: str, context: str = "") -> str:
    """向模型发送请求"""
    url = "http://127.0.0.1:1234/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer lm-studio"
    }
    
    # 准备提示
    messages = [
        {"role": "system", "content": "你是一个专门解答西班牙建筑规范问题的专家。请根据提供的规范内容，准确回答问题。"},
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

def load_example_context():
    """加载示例规范内容"""
    try:
        with open("processed_data/example.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
            section = data['data']['sections']['1']['data']
            
            # 格式化上下文
            context_parts = [
                f"章节：{section['title_es']}",
                f"内容：{section['content_es']}"
            ]
            
            # 添加要求
            if 'requirements' in section:
                context_parts.append("\n要求：")
                for req in section['requirements']:
                    context_parts.append(f"- {req['text_es']}")
                    
            return "\n".join(context_parts)
    except Exception as e:
        logger.error(f"加载示例数据时出错: {str(e)}")
        return ""

def main():
    print("\n=== 建筑规范问答演示 ===")
    print("(输入 'quit' 退出)")
    
    # 加载示例上下文
    context = load_example_context()
    if context:
        print("\n已加载规范内容：")
        print("-" * 50)
        print(context)
        print("-" * 50)
    
    while True:
        # 获取用户问题
        question = input("\n请输入您的问题: ").strip()
        if question.lower() in ['quit', 'exit', 'q']:
            break
            
        if not question:
            continue
            
        print("\n正在思考...")
        response = query_model(question, context)
        print("\n回答：")
        print("-" * 50)
        print(response)
        print("-" * 50)

if __name__ == "__main__":
    main() 