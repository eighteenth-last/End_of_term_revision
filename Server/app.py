"""
FastAPI 主应用程序
End_of_term_revision - 神阁卷藏
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import (
    subjects_router,
    questions_router,
    import_router,
    practice_router,
    error_router,
    model_router,
    auth_router,
    resource_router
)

# 创建 FastAPI 应用
app = FastAPI(
    title="End_of_term_revision API",
    description="神阁卷藏 - 支持多科目题库、AI 解析、错题集、自定义练习",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该指定具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth_router.router)
app.include_router(subjects_router.router)
app.include_router(questions_router.router)
app.include_router(import_router.router)
app.include_router(practice_router.router)
app.include_router(error_router.router)
app.include_router(model_router.router)
app.include_router(resource_router.router)


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    print("\n" + "="*60)
    print("🎓 神阁卷藏 API 启动成功!")
    print("="*60)
    print(f"📚 API 文档: http://localhost:8000/docs")
    print(f"🔧 健康检查: http://localhost:8000/health")
    print(f"⚡ 版本: 1.0.0")
    print("="*60 + "\n")


@app.get("/")
def root():
    """根路径"""
    return {
        "message": "Welcome to 神阁卷藏 API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """健康检查"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
