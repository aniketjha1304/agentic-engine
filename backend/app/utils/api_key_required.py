from fastapi import FastAPI, Header, HTTPException, Depends
from app.config.env import API_KEYS
import logging
from functools import wraps

logger = logging.getLogger(__name__)



async def api_key_required(x_api_key: str = Header(None)):
    if not x_api_key or x_api_key not in API_KEYS:
        logger.warning(f"Invalid or missing API key: {x_api_key}")
        raise HTTPException(status_code=401, detail="API key is missing or invalid")
    return x_api_key