# 建筑规范文档处理器

这个项目旨在将建筑规范文档（包含文本、表格、公式和编号系统）转换成适合AI模型处理或RAG系统使用的格式。

## 项目结构

```
building_code_processor/
├── src/
│   ├── __init__.py
│   ├── text_processor.py      # 文本处理模块
│   ├── table_processor.py     # 表格处理模块
│   ├── formula_processor.py   # 公式处理模块
│   ├── numbering_processor.py # 编号系统处理模块
│   └── utils.py              # 工具函数
├── tests/                    # 测试文件
├── examples/                 # 示例文件
├── requirements.txt          # 项目依赖
└── README.md                # 项目说明
```

## 功能特点

- 文本处理：提取和规范化文本内容
- 表格处理：识别和转换表格结构
- 公式处理：解析和标准化数学公式
- 编号系统处理：识别和处理文档的编号层次结构
- 输出格式：支持多种AI友好的输出格式（JSON、Markdown等）

## 安装

```bash
pip install -r requirements.txt
```

## 使用方法

待补充

## 开发状态

项目正在开发中

# 建筑规范AI问答网页版

本项目基于 Streamlit 实现建筑规范专业问答系统，支持中英文切换，适合国际化和老板体验。

## 在线体验

1. 将本项目上传到 GitHub。
2. 在 [Streamlit Community Cloud](https://streamlit.io/cloud) 选择仓库一键部署。
3. 入口文件为 `web_rag.py`。

## 本地运行

```bash
pip install -r requirements.txt
streamlit run web_rag.py
```

## 依赖
- streamlit
- requests

## 配置
请将 `web_rag.py` 中的 `API_URL` 改为你的后端API公网地址。 