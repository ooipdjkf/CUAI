from typing import Dict, List, Optional, Union
import json
from pathlib import Path
import torch
from transformers import AutoTokenizer, AutoModel
import numpy as np
from .gpt_teacher import GPTTeacher
from .language_utils import LanguageDetector
import asyncio
import logging

logger = logging.getLogger(__name__)

class BuildingCodeModel:
    """建筑规范解释模型的基类"""
    
    def __init__(self, 
                model_name: str = "PlanTL-GOB-ES/roberta-base-bne",
                use_gpt: bool = True,
                gpt_api_key: Optional[str] = None,
                gpt_model: str = "deepseek-r1-distill-qwen-7b",
                language: Optional[str] = None):
        """
        初始化模型
        Args:
            model_name: 预训练模型名称，默认使用西班牙语BERT模型
            use_gpt: 是否使用GPT教师模型
            gpt_api_key: GPT API密钥
            gpt_model: 使用的GPT模型名称
            language: 回答语言 ("es" 西班牙语, "zh" 中文)，如果为 None 则自动检测
        """
        # 初始化基础模型
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.default_language = language
        
        # 初始化GPT教师模型
        self.use_gpt = use_gpt
        if use_gpt:
            self.teacher = GPTTeacher(api_key=gpt_api_key, model=gpt_model)
        
        self.document_data = {}
        self.section_embeddings = {}
        self.formula_embeddings = {}
        self.requirement_embeddings = {}
        
    def load_document_data(self, json_path: str):
        """
        加载处理后的文档数据
        Args:
            json_path: JSON文件路径
        """
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.document_data = data
        
    def _get_text_embedding(self, text: str) -> np.ndarray:
        """
        获取文本的嵌入向量
        Args:
            text: 输入文本
        Returns:
            文本的嵌入向量
        """
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).numpy()[0]
        
    def build_embeddings(self):
        """构建章节、公式和要求的嵌入向量"""
        # 处理章节
        for section_id, section in self.document_data['data']['sections'].items():
            text = f"{section['data']['title_es']}\n{section['data']['content_es']}"
            self.section_embeddings[section_id] = self._get_text_embedding(text)
            
        # 处理公式
        for formula_id, formula in self.document_data['data']['formulas'].items():
            text = f"{formula['data']['expression']}\n{formula['data']['context_es']}"
            self.formula_embeddings[formula_id] = self._get_text_embedding(text)
            
        # 处理要求
        for section in self.document_data['data']['sections'].values():
            for req in section['data']['requirements']:
                text = f"{req['text_es']}"
                self.requirement_embeddings[req['text_es']] = self._get_text_embedding(text)
                
    def find_relevant_sections(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        查找与查询最相关的章节
        Args:
            query: 查询文本
            top_k: 返回的最相关章节数量
        Returns:
            相关章节列表
        """
        query_embedding = self._get_text_embedding(query)
        
        # 计算相似度
        similarities = {}
        for section_id, embedding in self.section_embeddings.items():
            similarity = np.dot(query_embedding, embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(embedding)
            )
            similarities[section_id] = similarity
            
        # 获取最相关的章节
        top_sections = sorted(similarities.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        results = []
        for section_id, score in top_sections:
            section = self.document_data['data']['sections'][section_id]
            results.append({
                'section_id': section_id,
                'title': section['data']['title_es'],
                'content': section['data']['content_es'],
                'score': float(score)
            })
            
        return results
        
    def find_relevant_formulas(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        查找与查询最相关的公式
        Args:
            query: 查询文本
            top_k: 返回的最相关公式数量
        Returns:
            相关公式列表
        """
        query_embedding = self._get_text_embedding(query)
        
        # 计算相似度
        similarities = {}
        for formula_id, embedding in self.formula_embeddings.items():
            similarity = np.dot(query_embedding, embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(embedding)
            )
            similarities[formula_id] = similarity
            
        # 获取最相关的公式
        top_formulas = sorted(similarities.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        results = []
        for formula_id, score in top_formulas:
            formula = self.document_data['data']['formulas'][formula_id]
            results.append({
                'formula_id': formula_id,
                'expression': formula['data']['expression'],
                'context': formula['data']['context_es'],
                'variables': formula['data']['variables'],
                'score': float(score)
            })
            
        return results
        
    def find_relevant_requirements(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        查找与查询最相关的要求
        Args:
            query: 查询文本
            top_k: 返回的最相关要求数量
        Returns:
            相关要求列表
        """
        query_embedding = self._get_text_embedding(query)
        
        # 计算相似度
        similarities = {}
        for text, embedding in self.requirement_embeddings.items():
            similarity = np.dot(query_embedding, embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(embedding)
            )
            similarities[text] = similarity
            
        # 获取最相关的要求
        top_requirements = sorted(similarities.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        results = []
        for text, score in top_requirements:
            results.append({
                'text': text,
                'score': float(score)
            })
            
        return results
        
    async def answer_question(self, question: str) -> Dict:
        """
        回答关于规范的问题
        Args:
            question: 问题文本
        Returns:
            包含答案和相关信息的字典
        """
        # 检测问题语言
        detected_lang = (
            self.default_language 
            if self.default_language is not None 
            else LanguageDetector.detect_language(question)
        )
        logger.info(f"Using language: {detected_lang} for question: {question[:50]}...")
        
        # 获取相关信息
        relevant_sections = self.find_relevant_sections(question, top_k=2)
        relevant_formulas = self.find_relevant_formulas(question, top_k=2)
        relevant_requirements = self.find_relevant_requirements(question, top_k=2)
        
        # 构建上下文
        context = {
            'relevant_sections': relevant_sections,
            'relevant_formulas': relevant_formulas,
            'relevant_requirements': relevant_requirements
        }
        
        # 使用GPT生成答案或使用基础模型
        if self.use_gpt:
            # 更新教师模型的语言设置
            self.teacher.language = detected_lang
            
            response = await self.teacher.generate_answer(question, context)
            answer = {
                'answer': response['answer'],
                'model_info': {
                    'model_used': response['model_used'],
                    'language': detected_lang,
                    'tokens_used': response.get('tokens_used', 0)
                },
                'relevant_sections': relevant_sections,
                'relevant_formulas': relevant_formulas,
                'relevant_requirements': relevant_requirements
            }
        else:
            # 使用基础模型的简单回答逻辑
            answer = {
                'answer': "基于相关内容的简单回答...",  # 这里可以实现更复杂的回答生成逻辑
                'model_info': {
                    'model_used': 'base_model',
                    'language': detected_lang,
                    'tokens_used': 0
                },
                'relevant_sections': relevant_sections,
                'relevant_formulas': relevant_formulas,
                'relevant_requirements': relevant_requirements
            }
        
        return answer
        
    def sync_answer_question(self, question: str) -> Dict:
        """
        同步版本的问答函数
        Args:
            question: 问题文本
        Returns:
            包含答案和相关信息的字典
        """
        return asyncio.run(self.answer_question(question)) 