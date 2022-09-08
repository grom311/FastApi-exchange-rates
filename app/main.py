from fastapi import FastAPI

from routers import currency


app = FastAPI()

app.include_router(currency.router)
