from typing import Dict, List, Optional
import requests
import json
from pathlib import Path
import logging
from .terminology import TerminologyTranslator

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GPTTeacher:
    """GPT教师模型，用于生成高质量答案和训练数据"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "deepseek-r1-distill-qwen-7b", use_local: bool = True, language: str = "es"):
        """
        初始化GPT教师模型
        Args:
            api_key: API密钥
            model: 使用的模型名称
            use_local: 是否使用本地LM Studio服务器
            language: 回答语言 ("es" 西班牙语, "zh" 中文)
        """
        self.model = model
        self.language = language
        
        # 多语言提示模板
        self.prompts = {
            "es": {
                "system_role": "Eres un experto en normativas de construcción españolas. Utiliza la terminología técnica adecuada en tus respuestas.",
                "intro": [
                    "Por favor, responde a la pregunta de manera profesional y precisa basándote en la información proporcionada.",
                    "Si no hay suficiente información, indícalo claramente.",
                    "\nInformación relevante:\n"
                ],
                "sections_header": "\nSecciones:",
                "section_format": "Sección {section_id}:\nTítulo: {title}\nContenido: {content}\n",
                "formulas_header": "\nFórmulas:",
                "formula_format": "Fórmula {formula_id}:\nExpresión: {expression}\nContexto: {context}\n",
                "variables_header": "Variables:",
                "variable_format": "- {var}: {desc}",
                "requirements_header": "\nRequisitos:",
                "requirement_format": "- {text}\n",
                "question_prefix": "\nPregunta:",
                "answer_instruction": "\nPor favor, proporciona una respuesta detallada con referencias a la normativa y utilizando la terminología técnica apropiada."
            },
            "zh": {
                "system_role": "你是一个专门解答西班牙建筑规范问题的专家。请在回答中使用准确的专业术语。",
                "intro": [
                    "请根据提供的相关内容，用专业且准确的方式回答问题。",
                    "如果内容中没有足够的信息，请明确指出。",
                    "\n相关内容：\n"
                ],
                "sections_header": "\n章节内容：",
                "section_format": "章节 {section_id}:\n标题: {title}\n内容: {content}\n",
                "formulas_header": "\n相关公式：",
                "formula_format": "公式 {formula_id}:\n表达式: {expression}\n上下文: {context}\n",
                "variables_header": "变量说明:",
                "variable_format": "- {var}: {desc}",
                "requirements_header": "\n规范要求：",
                "requirement_format": "- {text}\n",
                "question_prefix": "\n问题：",
                "answer_instruction": "\n请提供详细的答案，包括相关的规范依据，并使用准确的专业术语。"
            }
        }
        
        if use_local:
            self.api_url = "http://127.0.0.1:1234/v1/chat/completions"
            self.headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer lm-studio"
            }
        else:
            self.api_url = "https://api.openai.com/v1/chat/completions"
            self.headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
        
        self.cache_dir = Path("model_cache")
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_file = self.cache_dir / "gpt_responses.json"
        self.load_cache()
        
    def load_cache(self):
        """加载缓存的回答"""
        if self.cache_file.exists():
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                self.response_cache = json.load(f)
        else:
            self.response_cache = {}
            
    def save_cache(self):
        """保存回答到缓存"""
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.response_cache, f, ensure_ascii=False, indent=2)
            
    def generate_cache_key(self, question: str, context: Dict) -> str:
        """生成缓存键"""
        # 使用问题和上下文的关键信息生成缓存键
        key_parts = [question]
        
        if context.get('relevant_sections'):
            key_parts.extend(s['section_id'] for s in context['relevant_sections'])
            
        if context.get('relevant_formulas'):
            key_parts.extend(f['formula_id'] for f in context['relevant_formulas'])
            
        return "|".join(key_parts)
        
    def _translate_technical_terms(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        翻译文本中的专业术语
        Args:
            text: 输入文本
            source_lang: 源语言
            target_lang: 目标语言
        Returns:
            翻译后的文本
        """
        # 遍历所有术语类别
        for category in ["structural", "fire_protection", "materials"]:
            # 获取该类别的所有术语
            terms = TerminologyTranslator.get_all_terms(category, source_lang)
            
            # 替换所有匹配的术语
            for _, term in terms.items():
                translated_term = TerminologyTranslator.translate_term(term, category, source_lang, target_lang)
                if translated_term:
                    # 使用大小写不敏感的替换
                    text = text.replace(term.lower(), translated_term)
                    text = text.replace(term.upper(), translated_term.upper())
                    text = text.replace(term.capitalize(), translated_term.capitalize())
                    
        return text

    def format_prompt(self, question: str, context: Dict) -> str:
        """
        格式化提示文本
        Args:
            question: 问题
            context: 相关上下文
        Returns:
            格式化的提示文本
        """
        template = self.prompts[self.language]
        prompt = template["intro"]
        
        # 添加章节信息
        if context.get('relevant_sections'):
            prompt.append(template["sections_header"])
            for section in context['relevant_sections']:
                # 翻译章节内容
                translated_title = self._translate_technical_terms(section['title'], "es", self.language)
                translated_content = self._translate_technical_terms(section['content'], "es", self.language)
                
                prompt.append(template["section_format"].format(
                    section_id=section['section_id'],
                    title=translated_title,
                    content=translated_content
                ))
                
        # 添加公式信息
        if context.get('relevant_formulas'):
            prompt.append(template["formulas_header"])
            for formula in context['relevant_formulas']:
                # 翻译公式上下文
                translated_context = self._translate_technical_terms(formula['context'], "es", self.language)
                
                prompt.append(template["formula_format"].format(
                    formula_id=formula['formula_id'],
                    expression=formula['expression'],
                    context=translated_context
                ))
                if formula.get('variables'):
                    prompt.append(template["variables_header"])
                    for var, desc in formula['variables'].items():
                        # 翻译变量描述
                        translated_desc = self._translate_technical_terms(desc, "es", self.language)
                        prompt.append(template["variable_format"].format(
                            var=var,
                            desc=translated_desc
                        ))
                
        # 添加规范要求
        if context.get('relevant_requirements'):
            prompt.append(template["requirements_header"])
            for req in context['relevant_requirements']:
                # 翻译要求文本
                translated_text = self._translate_technical_terms(req['text'], "es", self.language)
                prompt.append(template["requirement_format"].format(
                    text=translated_text
                ))
                
        # 添加问题
        prompt.append(f"{template['question_prefix']}{question}")
        prompt.append(template["answer_instruction"])
        
        return "\n".join(prompt)
        
    async def generate_answer(self, question: str, context: Dict) -> Dict:
        """
        生成答案
        Args:
            question: 问题
            context: 相关上下文
        Returns:
            包含答案和元数据的字典
        """
        # 检查缓存
        cache_key = self.generate_cache_key(question, context)
        if cache_key in self.response_cache:
            logger.info("Using cached response")
            return self.response_cache[cache_key]
            
        # 准备提示
        prompt = self.format_prompt(question, context)
        
        try:
            # 准备请求数据
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": self.prompts[self.language]["system_role"]},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 1000,
                "n": 1
            }
            
            # 发送请求
            response = requests.post(self.api_url, headers=self.headers, json=data)
            response_data = response.json()
            
            # 提取答案
            answer = response_data['choices'][0]['message']['content']
            
            # 构建响应
            result = {
                'answer': answer,
                'model_used': self.model,
                'language': self.language,
                'tokens_used': response_data.get('usage', {}).get('total_tokens'),
                'context_info': {
                    'sections_used': [s['section_id'] for s in context.get('relevant_sections', [])],
                    'formulas_used': [f['formula_id'] for f in context.get('relevant_formulas', [])]
                }
            }
            
            # 缓存响应
            self.response_cache[cache_key] = result
            self.save_cache()
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            error_messages = {
                "es": "Lo siento, ha ocurrido un error al generar la respuesta. Por favor, inténtelo de nuevo más tarde.",
                "zh": "抱歉，生成答案时出现错误。请稍后再试。"
            }
            return {
                'error': str(e),
                'answer': error_messages[self.language]
            }
            
    async def generate_training_data(self, sections: List[Dict], n_samples: int = 10) -> List[Dict]:
        """
        生成训练数据
        Args:
            sections: 规范章节列表
            n_samples: 生成的样本数量
        Returns:
            训练数据列表
        """
        training_samples = []
        
        try:
            # 为每个章节生成问答对
            for section in sections:
                # 提取章节信息
                section_id = section.get('section_id', '')
                title = section.get('title', '')
                content = section.get('content', '')
                
                # 构建上下文
                context = {
                    'relevant_sections': [{
                        'section_id': section_id,
                        'title': title,
                        'content': content
                    }]
                }
                
                # 如果有公式，添加到上下文
                if 'formulas' in section:
                    context['relevant_formulas'] = section['formulas']
                
                # 如果有要求，添加到上下文
                if 'requirements' in section:
                    context['relevant_requirements'] = section['requirements']
                
                # 生成问题和答案
                for _ in range(n_samples // len(sections)):
                    # 使用GPT生成问答对
                    question = f"请解释{title}中的主要要求和规定。"
                    response = await self.generate_answer(question, context)
                    
                    if 'error' not in response:
                        sample = {
                            'question': question,
                            'answer': response['answer'],
                            'context': context,
                            'language': self.language,
                            'metadata': {
                                'section_id': section_id,
                                'model_used': response['model_used']
                            }
                        }
                        training_samples.append(sample)
                    
            logger.info(f"Generated {len(training_samples)} training samples")
            return training_samples
            
        except Exception as e:
            logger.error(f"Error generating training data: {str(e)}")
            return [] 