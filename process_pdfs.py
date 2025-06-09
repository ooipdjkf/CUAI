"""
处理docs目录下的所有PDF文件
"""
import os
from src.pdf_processor import PDFProcessor

def main():
    # 创建输出目录
    output_dir = "processed"
    os.makedirs(output_dir, exist_ok=True)
    
    # 创建PDF处理器
    processor = PDFProcessor()
    
    # 处理docs目录下的所有PDF文件
    docs_dir = "docs"
    for filename in os.listdir(docs_dir):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(docs_dir, filename)
            print(f"\n处理文件: {filename}")
            
            try:
                # 处理PDF文件
                result = processor.process_pdf(pdf_path)
                
                # 保存JSON格式
                json_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.json")
                processor.save_to_json(result, json_path)
                print(f"已保存JSON文件: {json_path}")
                
                # 保存Markdown格式
                md_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.md")
                processor.save_to_markdown(result, md_path)
                print(f"已保存Markdown文件: {md_path}")
                
            except Exception as e:
                print(f"处理文件 {filename} 时出错: {str(e)}")
                continue

if __name__ == "__main__":
    main() 