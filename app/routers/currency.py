import json
import zlib
from datetime import date
from pprint import pprint

import httpx
from aioredis import Redis
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Request,
    Response
)

from settings import REDIS_HOST, REDIS_PORT
from .logger import logger

router = APIRouter(
    prefix="/currency",
    tags=["currency from nbrb"],
    responses={404: {"description": "Not Found"}}
)

async def redis_connect():
    redis = await Redis.from_url(
        f"redis://{REDIS_HOST}:{REDIS_PORT}",
        max_connections=10,
        decode_responses=True
    )
    yield redis
    await redis.close()


@router.get("/rates")
async def get_exchange_rates(
        response: Response,
        request: Request,
        redis: Redis = Depends(redis_connect),
        ondate: date=date.today()):
    """"""
    logger.info(f"Request rates: {request.url}")
    key = str(ondate)
    get_cashe = await redis.get(key)
    if get_cashe is None:
        response = await response_body(ondate)
        await redis.set(key, json.dumps(response.json()))
        ret_str:str = f"Exchange rates on date {ondate} successful save."
        response.headers["CRC32"] = await decode_to_crc32(ret_str)
        logger.info(f"Response rates: {ret_str}")
        return {'response': ret_str}
    ret_str:str = f"Exchange rates on date {ondate} exists in our system."
    response.headers["CRC32"] = await decode_to_crc32(ret_str)
    logger.info(f"Response rates: {ret_str}")
    return {'response': ret_str}


@router.get("/currency_code")
async def get_exchange_rates_code(
        response: Response,
        request: Request,
        currency_code:int = Query(...),
        redis: Redis = Depends(redis_connect),
        ondate: date = date.today()):
    """"""
    logger.info(f"Request rates Cur_OfficialRate: {request.url}")
    key = str(ondate)
    get_cashe = await redis.get(key)
    if get_cashe is None:
        response = await response_body(ondate)

        await redis.set(key, json.dumps(response.json()))
        get_cashe = await redis.get(key)

    exch_rates_code = await get_cur_official_rate(get_cashe, currency_code)
    if exch_rates_code == -1:
        logger.info(f"Response rates Cur_OfficialRate: {currency_code} not exist.")
        return {'response': f"Response rates Cur_OfficialRate: {currency_code} not exist."}
    response.headers["CRC32"] = await decode_to_crc32(exch_rates_code)
    logger.info(f"Response rates Cur_OfficialRate: {exch_rates_code}")
    return {'Cur_OfficialRate': exch_rates_code}


async def decode_to_crc32(param):
    byte_val = str(param).encode()
    return str(zlib.crc32(byte_val))


async def response_body(ondate):
    api_url = f"https://www.nbrb.by/api/exrates/rates?periodicity=0"
    params = {'ondate': ondate}
    async with httpx.AsyncClient() as client:
        response = await client.get(api_url, params=params)
    return response

async def get_cur_official_rate(get_cashe, currency_code):
    json_cashe:list = json.loads(get_cashe)
    exch_rates_code = -1
    for i in json_cashe:
        if i.get('Cur_ID', 0) == currency_code:
            exch_rates_code = i.get('Cur_OfficialRate')
            break
    return exch_rates_code

def http_exception():
    """Return Exception with description."""
    return HTTPException(status_code=404, detail="Cur_ID not exist.")
