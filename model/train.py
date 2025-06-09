import argparse
from pathlib import Path
import json
import logging
from typing import List, Dict
import torch
from torch.utils.data import Dataset, DataLoader
from base_model import BuildingCodeModel

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BuildingCodeDataset(Dataset):
    """建筑规范数据集"""
    
    def __init__(self, json_paths: List[str]):
        """
        初始化数据集
        Args:
            json_paths: JSON文件路径列表
        """
        self.data = []
        self.load_data(json_paths)
        
    def load_data(self, json_paths: List[str]):
        """加载数据"""
        for path in json_paths:
            with open(path, 'r', encoding='utf-8') as f:
                doc_data = json.load(f)
                
            # 从章节创建训练样本
            for section in doc_data['data']['sections'].values():
                if section['data']['content_es']:
                    self.data.append({
                        'text': section['data']['content_es'],
                        'type': 'section',
                        'metadata': {
                            'id': section['data']['id'],
                            'title': section['data']['title_es']
                        }
                    })
                    
            # 从公式创建训练样本
            for formula in doc_data['data']['formulas'].values():
                if formula['data']['context_es']:
                    self.data.append({
                        'text': formula['data']['context_es'],
                        'type': 'formula',
                        'metadata': {
                            'id': formula['data']['id'],
                            'expression': formula['data']['expression']
                        }
                    })
                    
            # 从要求创建训练样本
            for section in doc_data['data']['sections'].values():
                for req in section['data']['requirements']:
                    if req['text_es']:
                        self.data.append({
                            'text': req['text_es'],
                            'type': 'requirement',
                            'metadata': {
                                'section_id': section['data']['id']
                            }
                        })
                        
    def __len__(self):
        return len(self.data)
        
    def __getitem__(self, idx):
        return self.data[idx]

def train_model(args):
    """
    训练模型
    Args:
        args: 命令行参数
    """
    # 创建输出目录
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 加载数据
    logger.info("Loading dataset...")
    dataset = BuildingCodeDataset(args.input_files)
    dataloader = DataLoader(dataset, batch_size=args.batch_size, shuffle=True)
    
    # 初始化模型
    logger.info("Initializing model...")
    model = BuildingCodeModel(args.model_name)
    
    # 加载文档数据
    for file_path in args.input_files:
        model.load_document_data(file_path)
    
    # 构建嵌入向量
    logger.info("Building embeddings...")
    model.build_embeddings()
    
    # 保存模型
    logger.info("Saving model...")
    torch.save(model.state_dict(), output_dir / 'model.pt')
    
    # 评估模型
    logger.info("Evaluating model...")
    evaluate_model(model, args.test_questions)
    
def evaluate_model(model: BuildingCodeModel, test_questions: List[str]):
    """
    评估模型
    Args:
        model: 训练好的模型
        test_questions: 测试问题列表
    """
    for question in test_questions:
        logger.info(f"\nQuestion: {question}")
        answer = model.answer_question(question)
        
        # 打印生成的答案
        logger.info("\nGenerated Answer:")
        logger.info(answer['answer'])
        
        # 打印相关章节
        logger.info("\nRelevant sections:")
        for section in answer['relevant_sections']:
            logger.info(f"- Section {section['section_id']} (score: {section['score']:.3f})")
            logger.info(f"  Title: {section['title'][:100]}...")
            
        # 打印相关公式
        logger.info("\nRelevant formulas:")
        for formula in answer['relevant_formulas']:
            logger.info(f"- Formula {formula['formula_id']} (score: {formula['score']:.3f})")
            logger.info(f"  Expression: {formula['expression'][:100]}...")
            
        # 打印相关要求
        logger.info("\nRelevant requirements:")
        for req in answer['relevant_requirements']:
            logger.info(f"- Requirement (score: {req['score']:.3f})")
            logger.info(f"  Text: {req['text'][:100]}...")
            
        logger.info("\n" + "="*80 + "\n")

def main():
    parser = argparse.ArgumentParser(description='Train building code model')
    parser.add_argument('--input_files', nargs='+', required=True,
                      help='Input JSON files')
    parser.add_argument('--output_dir', required=True,
                      help='Output directory')
    parser.add_argument('--model_name', default="PlanTL-GOB-ES/roberta-base-bne",
                      help='Pre-trained model name')
    parser.add_argument('--batch_size', type=int, default=8,
                      help='Batch size')
    parser.add_argument('--test_questions', nargs='+', default=[
        "¿Cuáles son los requisitos para la protección contra incendios?",
        "¿Cómo se calcula la resistencia estructural?",
        "¿Qué tipos de materiales se pueden utilizar?"
    ], help='Test questions for evaluation')
    
    args = parser.parse_args()
    train_model(args)

if __name__ == '__main__':
    main() 