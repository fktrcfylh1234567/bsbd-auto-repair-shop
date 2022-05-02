from fastapi import FastAPI

import reports
import staffers
import discount_cards
import services
import materials
import purchases
import orders

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(staffers.router)
app.include_router(discount_cards.router)
app.include_router(services.router)
app.include_router(materials.router)
app.include_router(purchases.router)
app.include_router(orders.router)
app.include_router(reports.router)
print("Start server")


@app.get("/")
async def root():
    return "Server works!"
