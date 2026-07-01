from motor.motor_asyncio import (
    AsyncIOMotorClient
)

client = AsyncIOMotorClient(
    "mongodb://localhost:27017"
)

db = client["psy_ai"]


def get_db():
    return db