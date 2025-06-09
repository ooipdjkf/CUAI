import os
import json
from pathlib import Path
import logging
from .base_model import BuildingCodeModel
from .language_utils import LanguageDetector

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_language_detection():
    """测试语言检测功能"""
    test_texts = {
        "es": [
            "¿Cuáles son los requisitos para la protección contra incendios?",
            "Necesito información sobre la construcción de muros.",
            "¿Cómo se calcula la resistencia de una viga?"
        ],
        "zh": [
            "建筑防火要求是什么？",
            "我需要了解墙体建设的相关信息。",
            "如何计算梁的强度？"
        ]
    }
    
    logger.info("\n测试语言检测功能...")
    for expected_lang, texts in test_texts.items():
        for text in texts:
            detected_lang = LanguageDetector.detect_language(text)
            logger.info(f"\n文本: {text}")
            logger.info(f"预期语言: {expected_lang}")
            logger.info(f"检测语言: {detected_lang}")
            logger.info("检测结果: " + ("✓" if detected_lang == expected_lang else "✗"))

def test_model():
    """测试模型功能"""
    # 测试问题
    test_questions = [
        "¿Cuáles son los requisitos para la protección contra incendios en edificios industriales?",
        "工业建筑的防火要求是什么？",
        "¿Cómo se calcula la resistencia estructural de una viga de acero?",
        "如何计算钢梁的结构强度？",
        "¿Qué tipos de materiales se pueden utilizar en la construcción de muros cortafuegos?",
        "防火墙可以使用哪些材料建造？"
    ]
    
    # 初始化模型（不指定默认语言，使用自动检测）
    model = BuildingCodeModel(
        use_gpt=True,
        gpt_api_key="lm-studio",
        gpt_model="deepseek-r1-distill-qwen-7b"
    )
    
    # 加载测试数据
    processed_data_dir = Path("processed_data")
    json_files = list(processed_data_dir.glob("*.json"))
    if not json_files:
        logger.error("未找到处理后的数据文件")
        return
        
    # 加载最新的数据文件
    latest_file = max(json_files, key=lambda x: x.stat().st_mtime)
    model.load_document_data(str(latest_file))
    
    # 构建嵌入向量
    logger.info("构建嵌入向量...")
    model.build_embeddings()
    
    # 测试回答
    logger.info("\n开始测试问答功能...")
    for question in test_questions:
        logger.info(f"\n问题: {question}")
        
        try:
            # 获取答案
            response = model.sync_answer_question(question)
            
            # 打印答案
            logger.info("\n生成的答案:")
            logger.info(response['answer'])
            
            # 打印模型信息
            logger.info("\n模型信息:")
            logger.info(f"使用的模型: {response['model_info']['model_used']}")
            logger.info(f"检测的语言: {response['model_info']['language']}")
            if response['model_info'].get('tokens_used'):
                logger.info(f"使用的令牌数: {response['model_info']['tokens_used']}")
            
            # 打印相关内容统计
            logger.info("\n相关内容统计:")
            logger.info(f"相关章节数: {len(response['relevant_sections'])}")
            logger.info(f"相关公式数: {len(response['relevant_formulas'])}")
            logger.info(f"相关要求数: {len(response['relevant_requirements'])}")
            
            logger.info("\n" + "="*80)
            
        except Exception as e:
            logger.error(f"处理问题时出错: {str(e)}")
            
if __name__ == "__main__":
    # 先测试语言检测
    test_language_detection()
    
    # 再测试模型功能
    test_model() 