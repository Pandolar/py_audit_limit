# python3
# -- coding: utf-8 --
# -------------------------------
# @Author : Terry
# @File : main.py
# @Time : 2024/10/15 下午6:26
# -------------------------------
from fastapi import FastAPI
from api.audit import router as audit_router
from config import PORT

app = FastAPI()

app.include_router(audit_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)