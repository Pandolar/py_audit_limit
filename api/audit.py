# python3
# -- coding: utf-8 --
# -------------------------------
# @Author : Terry
# @File : audit.py.py
# @Time : 2024/10/15 下午6:26
# -------------------------------
from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from config import OAIKEY, MODERATION, ForbiddenWords
import httpx
from .rate_limit import RateLimiter, get_rate_limit

router = APIRouter()


class Message(BaseModel):
    content: dict


class AuditRequest(BaseModel):
    action: str
    model: str
    messages: List[Message]


async def check_moderation(prompt: str):
    if not OAIKEY or not prompt:
        return False

    async with httpx.AsyncClient() as client:
        response = await client.post(
            MODERATION,
            headers={"Authorization": f"Bearer {OAIKEY}", "Content-Type": "application/json"},
            json={"input": prompt}
        )
        resp_json = response.json()
        return resp_json.get("results", [{}])[0].get("flagged", False)


@router.post("/audit")
async def audit(request: Request, audit_request: AuditRequest, rate_limiter: RateLimiter = Depends(get_rate_limit)):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    prompt = audit_request.messages[0].content.get("parts", [""])[0]

    if any(word in prompt for word in ForbiddenWords):
        raise HTTPException(status_code=400, detail="请珍惜账号,不要提问违禁内容.")

    if await check_moderation(prompt):
        raise HTTPException(status_code=400, detail={"code": "flagged_by_moderation", "message": "This content may violate OpenAI Usage Policies."})

    await rate_limiter.acquire(token, audit_request.model)
    return {"status": "ok"}