import json
import zlib
from datetime import date, timedelta

import httpx
from aioredis import Redis
from fastapi import (
    APIRouter,
    Depends,
    Query,
    Request,
    Response
)

from settings import REDIS_HOST, REDIS_PORT
from .logger import logger

router = APIRouter(
    prefix="/currency",
    tags=["Сurrency from nbrb"],
    responses={404: {"description": "Not Found"}}
)

async def redis_connect():
    """Method returns generator Redis connections."""
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
    """
        Endpoint get info from NBRB by exchange rates on date.
        The information is stored in Redis, if it exists, return message about it..
    """
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
    """
        Endpoint get info from NBRB by exchange rates on date and code currency.
        The information is stored in Redis, if it exists, return it from Redis.
    """
    logger.info(f"Request rates Cur_OfficialRate: {request.url}")
    get_cashe = await redis_cashe(ondate, redis)
    exch_rates_code = await get_cur_official_rate(get_cashe, currency_code)

    if exch_rates_code == -1:
        logger.info(f"Response rates Cur_OfficialRate: {currency_code} not exist.")
        ret = {'response': f"Response rates Cur_OfficialRate: {currency_code} not exist."}
        response.headers["CRC32"] = await decode_to_crc32(ret)
        return ret
    ch_course = await course_change_day(exch_rates_code, currency_code, ondate, redis)
    ret = {'Cur_OfficialRate': exch_rates_code, 'ch_course': ch_course}
    response.headers["CRC32"] = await decode_to_crc32(ret)
    logger.info(f"Response rates Cur_OfficialRate: {ret}")

    return ret


async def course_change_day(exch_rates_code, currency_code, ondate, redis):
    """Method returns delta course change by 1 day."""
    yestaday = ondate - timedelta(days=1)
    get_cashe = await redis_cashe(yestaday, redis)
    yestaday_exch_rates_code = await get_cur_official_rate(get_cashe, currency_code)

    return round(exch_rates_code-yestaday_exch_rates_code, 4)


async def redis_cashe(ondate, redis):
    """Methos returns cashe from Redis, if not exist, set in Redis."""
    key = str(ondate)
    get_cashe = await redis.get(key)

    if get_cashe is None:
        response = await response_body(ondate)
        await redis.set(key, json.dumps(response.json()))
        get_cashe = await redis.get(key)
    return get_cashe


async def decode_to_crc32(param):
    """Decode to the crc32 from any str."""
    byte_val = str(param).encode()
    return str(zlib.crc32(byte_val))


async def response_body(ondate):
    """Method returns info about currency rates from nbrb api."""
    api_url = "https://www.nbrb.by/api/exrates/rates?periodicity=0"
    params = {'ondate': ondate}
    async with httpx.AsyncClient() as client:
        response = await client.get(api_url, params=params)
    return response

async def get_cur_official_rate(get_cashe, currency_code):
    """Find the exchange rate from the cache by the given code."""
    json_cashe:list = json.loads(get_cashe)
    exch_rates_code = -1
    for i in json_cashe:
        if i.get('Cur_ID', 0) == currency_code:
            exch_rates_code = i.get('Cur_OfficialRate')
            break
    return exch_rates_code
