from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class TerminologyTranslator:
    """建筑领域专业术语翻译器"""
    
    # 专业术语词典
    TERMS = {
        # 结构术语
        "structural": {
            "es": {
                "beam": "viga",
                "column": "columna",
                "slab": "losa",
                "foundation": "cimentación",
                "load": "carga",
                "stress": "tensión",
                "strain": "deformación",
                "reinforcement": "refuerzo",
                "steel": "acero",
                "concrete": "hormigón",
                "compression": "compresión",
                "tension": "tracción",
                "bending": "flexión",
                "shear": "cortante"
            },
            "zh": {
                "beam": "梁",
                "column": "柱",
                "slab": "板",
                "foundation": "基础",
                "load": "荷载",
                "stress": "应力",
                "strain": "应变",
                "reinforcement": "钢筋",
                "steel": "钢材",
                "concrete": "混凝土",
                "compression": "压力",
                "tension": "拉力",
                "bending": "弯曲",
                "shear": "剪力"
            }
        },
        
        # 防火术语
        "fire_protection": {
            "es": {
                "fire resistance": "resistencia al fuego",
                "fire wall": "muro cortafuegos",
                "fire door": "puerta cortafuegos",
                "fire escape": "escalera de emergencia",
                "sprinkler": "rociador",
                "smoke detector": "detector de humo",
                "fire alarm": "alarma de incendios",
                "emergency exit": "salida de emergencia",
                "fire extinguisher": "extintor",
                "evacuation": "evacuación",
                "fire compartment": "compartimento de incendios",
                "fire rating": "clasificación de resistencia al fuego",
                "fire protection": "protección contra incendios",
                "fire safety": "seguridad contra incendios"
            },
            "zh": {
                "fire resistance": "耐火性能",
                "fire wall": "防火墙",
                "fire door": "防火门",
                "fire escape": "消防通道",
                "sprinkler": "喷淋头",
                "smoke detector": "烟感探测器",
                "fire alarm": "火灾报警器",
                "emergency exit": "紧急出口",
                "fire extinguisher": "灭火器",
                "evacuation": "疏散",
                "fire compartment": "防火分区",
                "fire rating": "耐火等级",
                "fire protection": "消防防护",
                "fire safety": "消防安全"
            }
        },
        
        # 材料术语
        "materials": {
            "es": {
                "timber": "madera",
                "brick": "ladrillo",
                "mortar": "mortero",
                "glass": "vidrio",
                "insulation": "aislamiento",
                "waterproofing": "impermeabilización",
                "coating": "revestimiento",
                "paint": "pintura",
                "ceramic": "cerámica",
                "plastic": "plástico",
                "aluminum": "aluminio",
                "copper": "cobre",
                "composite": "compuesto",
                "aggregate": "árido"
            },
            "zh": {
                "timber": "木材",
                "brick": "砖",
                "mortar": "砂浆",
                "glass": "玻璃",
                "insulation": "保温材料",
                "waterproofing": "防水",
                "coating": "涂层",
                "paint": "油漆",
                "ceramic": "陶瓷",
                "plastic": "塑料",
                "aluminum": "铝",
                "copper": "铜",
                "composite": "复合材料",
                "aggregate": "骨料"
            }
        }
    }
    
    @staticmethod
    def translate_term(term: str, category: str, source_lang: str, target_lang: str) -> Optional[str]:
        """
        翻译专业术语
        Args:
            term: 术语
            category: 术语类别 ("structural", "fire_protection", "materials")
            source_lang: 源语言
            target_lang: 目标语言
        Returns:
            翻译后的术语，如果未找到则返回 None
        """
        try:
            # 确保类别存在
            if category not in TerminologyTranslator.TERMS:
                logger.warning(f"Unknown category: {category}")
                return None
                
            # 获取源语言术语字典
            source_terms = TerminologyTranslator.TERMS[category][source_lang]
            target_terms = TerminologyTranslator.TERMS[category][target_lang]
            
            # 查找术语
            for src_term, src_translation in source_terms.items():
                if term.lower() == src_translation.lower():
                    # 找到匹配的源语言术语，返回目标语言翻译
                    return target_terms[src_term]
                    
            logger.debug(f"Term not found: {term} in category {category}")
            return None
            
        except Exception as e:
            logger.error(f"Error translating term: {str(e)}")
            return None
            
    @staticmethod
    def get_all_terms(category: str, language: str) -> Dict[str, str]:
        """
        获取指定类别和语言的所有术语
        Args:
            category: 术语类别
            language: 语言
        Returns:
            术语字典
        """
        try:
            if category in TerminologyTranslator.TERMS:
                return TerminologyTranslator.TERMS[category][language]
            return {}
        except Exception as e:
            logger.error(f"Error getting terms: {str(e)}")
            return {} 