from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from ..schemas import Shortener
from ..crud import generate_short_code, get_long_url, get_all_urls
from ..dependencies import rate_limit
from ..database import get_db_connection
from ..config import settings

router = APIRouter(tags=["shortener"])

@router.post("/shorten/", dependencies=[Depends(rate_limit)])
async def shorten_url(
    shortener: Shortener,
    conn=Depends(get_db_connection)
):
    short_code = await generate_short_code(conn, str(shortener.long_url))
    return {"short_url": f"{settings.HOST_NAME}/{short_code}"}

# @router.get("/api/urls")
# async def get_all_urls_endpoint(conn=Depends(get_db_connection)):
#     urls = await get_all_urls(conn)
#     return [{"long_url": row[0], "short_code": row[1]} for row in urls]
