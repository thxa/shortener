from pydantic import BaseModel, HttpUrl

class Shortener(BaseModel):
    long_url: HttpUrl
