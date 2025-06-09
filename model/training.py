from transformers import Trainer, TrainingArguments
from datasets import Dataset
import pandas as pd
import torch
from typing import List, Dict

class CTEModelTrainer:
    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer
        
    def prepare_training_data(self, 
                            questions: List[str], 
                            contexts: List[str], 
                            answers: List[Dict]):
        """准备训练数据"""
        training_data = {
            'question': questions,
            'context': contexts,
            'answer': answers
        }
        return Dataset.from_dict(training_data)
        
    def tokenize_data(self, examples):
        """对数据进行分词处理"""
        questions = [q.strip() for q in examples["question"]]
        contexts = [c.strip() for c in examples["context"]]
        
        # 对问题和上下文进行编码
        tokenized = self.tokenizer(
            questions,
            contexts,
            max_length=384,
            truncation="only_second",
            stride=128,
            return_overflowing_tokens=True,
            return_offsets_mapping=True,
            padding="max_length"
        )
        
        return tokenized
        
    def train(self, 
              train_dataset: Dataset,
              output_dir: str = "./trained_model",
              num_epochs: int = 3,
              batch_size: int = 16,
              learning_rate: float = 2e-5):
        """训练模型"""
        
        # 设置训练参数
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=num_epochs,
            per_device_train_batch_size=batch_size,
            learning_rate=learning_rate,
            weight_decay=0.01,
            logging_dir='./logs',
            logging_steps=100,
            save_strategy="epoch"
        )
        
        # 初始化训练器
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            tokenizer=self.tokenizer,
            data_collator=self.collate_fn
        )
        
        # 开始训练
        trainer.train()
        
        # 保存模型
        trainer.save_model()
        
    def collate_fn(self, features):
        """准备批次数据"""
        batch = self.tokenizer.pad(
            features,
            padding=True,
            return_tensors="pt",
        )
        
        return batch
        
    def prepare_example_data(self):
        """准备示例训练数据"""
        questions = [
            "什么是DB-SE文档?",
            "马德里属于哪个气候区?",
            "建筑物的防火要求是什么?"
        ]
        
        contexts = [
            "DB-SE是结构安全基本文档,规定了建筑结构安全的基本要求...",
            "马德里位于D3气候区,具有较高的供暖需求...",
            "根据DB-SI文档,建筑物需要满足特定的防火要求..."
        ]
        
        answers = [
            {"text": "结构安全基本文档", "answer_start": 6},
            {"text": "D3气候区", "answer_start": 5},
            {"text": "需要满足特定的防火要求", "answer_start": 15}
        ]
        
        return questions, contexts, answers
        
def main():
    """示例训练流程"""
    from transformers import AutoModelForQuestionAnswering, AutoTokenizer
    
    # 初始化模型和分词器
    model = AutoModelForQuestionAnswering.from_pretrained("bert-base-multilingual-cased")
    tokenizer = AutoTokenizer.from_pretrained("bert-base-multilingual-cased")
    
    # 创建训练器
    trainer = CTEModelTrainer(model, tokenizer)
    
    # 准备示例数据
    questions, contexts, answers = trainer.prepare_example_data()
    
    # 创建数据集
    dataset = trainer.prepare_training_data(questions, contexts, answers)
    
    # 训练模型
    trainer.train(dataset)
    
if __name__ == "__main__":
    main() 