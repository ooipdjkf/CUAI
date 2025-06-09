from transformers import AutoModelForQuestionAnswering, AutoTokenizer
import torch
import json
import os

class CTEExplainer:
    def __init__(self):
        """初始化CTE解释器模型"""
        self.tokenizer = AutoTokenizer.from_pretrained("bert-base-multilingual-cased")
        self.model = AutoModelForQuestionAnswering.from_pretrained("bert-base-multilingual-cased")
        
        # 加载CTE规范知识库
        self.knowledge_base = self._load_knowledge_base()
        
    def _load_knowledge_base(self):
        """加载CTE规范知识库"""
        knowledge_base = {
            "基本文档": {
                "DB-SE": "结构安全基本文档",
                "DB-SI": "火灾安全基本文档",
                "DB-SUA": "使用安全和可访问性基本文档",
                "DB-HS": "健康基本文档",
                "DB-HR": "噪声防护基本文档",
                "DB-HE": "节能基本文档"
            },
            "气候区域": {
                "A": {"HDD": 794, "CDD": 1089},
                "B3": {"HDD": 1181, "CDD": 1039},
                "C2": {"HDD": 1300, "CDD": 699},
                "D3": {"HDD": 1862, "CDD": 871}
            }
        }
        return knowledge_base
    
    def answer_question(self, question: str) -> str:
        """回答关于CTE的问题"""
        # 对问题进行分类
        if "气候区" in question:
            return self._handle_climate_question(question)
        elif any(doc in question for doc in self.knowledge_base["基本文档"].keys()):
            return self._handle_document_question(question)
        else:
            return self._handle_general_question(question)
            
    def _handle_climate_question(self, question: str) -> str:
        """处理关于气候区域的问题"""
        for zone, data in self.knowledge_base["气候区域"].items():
            if zone in question:
                return f"气候区{zone}的供暖度日数(HDD)为{data['HDD']}, 制冷度日数(CDD)为{data['CDD']}"
        return "请指定具体的气候区域(A, B3, C2, D3)"
        
    def _handle_document_question(self, question: str) -> str:
        """处理关于基本文档的问题"""
        for doc, desc in self.knowledge_base["基本文档"].items():
            if doc in question:
                return f"{doc}是{desc},是CTE的重要组成部分"
        return "请指定具体的基本文档(DB-SE, DB-SI, DB-SUA, DB-HS, DB-HR, DB-HE)"
        
    def _handle_general_question(self, question: str) -> str:
        """处理一般性问题"""
        # 使用Transformer模型生成回答
        inputs = self.tokenizer(question, return_tensors="pt")
        outputs = self.model(**inputs)
        
        # 这里简化处理,实际应用中需要更复杂的答案生成逻辑
        return "CTE是西班牙的主要建筑规范,包含多个基本文档,涵盖结构安全、火灾安全、节能等方面的要求。"
        
    def get_requirements(self, climate_zone: str, building_type: str) -> dict:
        """获取特定气候区域和建筑类型的要求"""
        requirements = {
            "thermal_transmittance": self._get_thermal_requirements(climate_zone),
            "ventilation": self._get_ventilation_requirements(building_type),
            "energy_efficiency": self._get_energy_requirements(climate_zone)
        }
        return requirements
        
    def _get_thermal_requirements(self, climate_zone: str) -> dict:
        """获取热工要求"""
        # 简化的热工要求示例
        requirements = {
            "A": {"wall": 0.94, "roof": 0.50, "floor": 0.53},
            "B3": {"wall": 0.82, "roof": 0.45, "floor": 0.52},
            "C2": {"wall": 0.73, "roof": 0.41, "floor": 0.50},
            "D3": {"wall": 0.66, "roof": 0.38, "floor": 0.49}
        }
        return requirements.get(climate_zone, {})
        
    def _get_ventilation_requirements(self, building_type: str) -> dict:
        """获取通风要求"""
        # 简化的通风要求示例
        requirements = {
            "residential": {"min_air_changes": 0.5, "kitchen_extract": 50},
            "office": {"min_fresh_air": 12.5, "min_air_changes": 0.8}
        }
        return requirements.get(building_type, {})
        
    def _get_energy_requirements(self, climate_zone: str) -> dict:
        """获取能源效率要求"""
        # 简化的能源效率要求示例
        requirements = {
            "A": {"max_energy_demand": 40, "min_renewable": 60},
            "B3": {"max_energy_demand": 45, "min_renewable": 55},
            "C2": {"max_energy_demand": 50, "min_renewable": 50},
            "D3": {"max_energy_demand": 60, "min_renewable": 40}
        }
        return requirements.get(climate_zone, {}) 