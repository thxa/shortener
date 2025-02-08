from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from ..crud import get_long_url
from ..dependencies import rate_limit
from ..database import get_db_connection

router = APIRouter(tags=["redirect"])

@router.get("/{short_code}", dependencies=[Depends(rate_limit)])
async def redirect_to_long_url(short_code: str, conn=Depends(get_db_connection)):
    long_url = await get_long_url(conn, short_code)
    if not long_url:
        raise HTTPException(status_code=404, detail="Short URL not found")
    return RedirectResponse(url=long_url, status_code=302)
