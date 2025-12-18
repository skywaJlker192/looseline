from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import Base, engine
from .routers import bets, coupons

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Looseline Betting API")

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

app.include_router(bets.router)
app.include_router(coupons.router)


@app.get("/health", tags=["service"])
def health_check():
  return {"status": "ok"}


