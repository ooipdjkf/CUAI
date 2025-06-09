"""
示例脚本：展示如何使用建筑规范文档处理器
"""
from src import BuildingCodeProcessor

def main():
    # 创建处理器实例
    processor = BuildingCodeProcessor()
    
    # 示例文档内容
    sample_text = """
1 总则
1.1 适用范围
本规范适用于新建、改建和扩建的建筑工程。

1.2 基本要求
建筑工程应符合以下基本要求：
- 安全性
- 适用性
- 耐久性

2 结构设计
2.1 荷载计算
结构设计应考虑以下荷载：
- 永久荷载
- 可变荷载
- 偶然荷载

2.2 计算公式
基本承载力计算公式：
$$R = \gamma_R \cdot R_k$$
其中：
- R 为设计承载力
- γR 为承载力分项系数
- Rk 为标准承载力

表2.1 承载力分项系数
| 荷载类型 | 分项系数 |
|---------|---------|
| 永久荷载 | 1.35    |
| 可变荷载 | 1.50    |
| 偶然荷载 | 1.00    |

3 材料要求
3.1 混凝土
混凝土强度等级不应低于C20。

3.2 钢筋
钢筋应符合以下要求：
- 屈服强度：≥400MPa
- 伸长率：≥14%
"""
    
    # 处理文档
    result = processor.process_document(sample_text)
    
    # 输出JSON格式
    print("JSON格式输出：")
    print(processor.to_json())
    print("\n")
    
    # 输出Markdown格式
    print("Markdown格式输出：")
    print(processor.to_markdown())

if __name__ == "__main__":
    main() 