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
    print("audit_request",audit_request)
    print("request.headers:", request.headers)
    # Headers({'host': '159.138.154.126:19892', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36', 'content-length': '908', 'authorization': 'Bearer usertest', 'carid': 'testcar', 'chatgpt-account-id': '', 'content-type': 'application/json', 'cookie': 'oai-did=f7e9bd07-5be3-449a-b7e6-0f98bed097bd; oai-nav-state=1; timestamp=1728569653955; xtoken=5ac2eab0-2c80-484d-a9d5-a0bac5e19316; xuserid=19; gfsessionid=1fk579d1itzu3bd4wh1yatujvo2004ca; _dd_s=logs=1&id=5b7b084e-988b-474a-bb37-01cbcf9e7aad&created=1729004818231&expire=1729005942510', 'referer': 'https://ts.183ai.com/', 'traceparent': '00-4c827b24eca8fe1749da1b6054a721c0-952e2c5bab2f2eaf-01', 'accept-encoding': 'gzip', 'connection': 'close'})
    usertoken = request.headers.get("Authorization", "").replace("Bearer ", "")
    # audit_request action='variant' model='o1-mini' messages=[Message(content={'content_type': 'text', 'parts': ['who are u？']})]
    prompt = audit_request.messages[0].content.get("parts", [""])[0]

    if any(word in prompt for word in ForbiddenWords):
        raise HTTPException(status_code=400, detail="请珍惜账号,不要提问违禁内容.")

    if await check_moderation(prompt):
        raise HTTPException(status_code=400, detail={"code": "flagged_by_moderation", "message": "This content may violate OpenAI Usage Policies."})

    await rate_limiter.acquire(usertoken, audit_request.model)
    return {"status": "ok"}
@router.get("/")
@router.get("/audit")
async def root():
    return {"message": "Hello, Star Limt Server Is Ready"}