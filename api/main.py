from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
import sys
import os

# 添加模型目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model.cte_model import CTEExplainer

app = FastAPI(
    title="西班牙建筑规范解释API",
    description="基于机器学习的西班牙建筑规范(CTE)解释系统",
    version="1.0.0"
)

# 初始化模型
model = CTEExplainer()

class Question(BaseModel):
    text: str
    
class RequirementsRequest(BaseModel):
    climate_zone: str
    building_type: str
    
@app.post("/answer", response_model=Dict[str, str])
async def answer_question(question: Question):
    """
    回答关于CTE的问题
    """
    try:
        answer = model.answer_question(question.text)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/requirements", response_model=Dict)
async def get_requirements(request: RequirementsRequest):
    """
    获取特定气候区域和建筑类型的要求
    """
    try:
        requirements = model.get_requirements(
            request.climate_zone,
            request.building_type
        )
        return requirements
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
@app.get("/documents")
async def get_documents():
    """
    获取CTE基本文档列表
    """
    try:
        return model.knowledge_base["基本文档"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
@app.get("/climate-zones")
async def get_climate_zones():
    """
    获取气候区域信息
    """
    try:
        return model.knowledge_base["气候区域"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 