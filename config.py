# python3
# -- coding: utf-8 --
# -------------------------------
# @Author : Terry
# @File : config.py.py
# @Time : 2024/10/15 下午6:27
# -------------------------------
import os
from typing import List

PORT = int(os.getenv("PORT", "8080"))
ForbiddenWords: List[str] = []
OAIKEY = os.getenv("OAIKEY", "")
MODERATION = os.getenv("MODERATION", "https://gateway.ai.cloudflare.com/v1/040ac2002b4dd67637e97c628feb3484/xyhelper/openai/moderations")

def get_config(key: str, default: str) -> str:
    return os.getenv(key, default)

# 读取禁止词
keywords_file = "data/keywords.txt"
if os.path.exists(keywords_file):
    with open(keywords_file, "r") as f:
        ForbiddenWords = [line.strip() for line in f if line.strip()]