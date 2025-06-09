import requests
import json

# API 配置
API_URL = "http://127.0.0.1:1234/v1/chat/completions"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer lm-studio"
}

# 测试问题
test_questions = [
    "¿Cuáles son los requisitos para la protección contra incendios en edificios industriales?",
]

# 测试回答
for question in test_questions:
    print(f"\n问题: {question}")
    
    try:
        # 准备请求数据
        data = {
            "model": "deepseek-r1-distill-qwen-7b",
            "messages": [
                {"role": "system", "content": "你是一个专门解答西班牙建筑规范问题的专家助手。"},
                {"role": "user", "content": question}
            ],
            "temperature": 0.7,
            "max_tokens": 1000,
            "n": 1
        }
        
        # 发送请求
        response = requests.post(API_URL, headers=HEADERS, json=data)
        response_data = response.json()
        
        # 打印答案
        print("\n生成的答案:")
        print(response_data['choices'][0]['message']['content'])
        
    except Exception as e:
        print(f"处理问题时出错: {str(e)}") 