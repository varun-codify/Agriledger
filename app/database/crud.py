import logging
from app.database.connection import get_db
from app.database.models import (
    User,
    Cattle,
    Crop,
    Transaction,
    BreedingCycle,
    CoconutSale,
    MilkSale,
)
from pymongo.errors import PyMongoError

SEED_USERS = [
    {"name": "Admin User", "email": "admin@example.com", "password": "password123"}
]


def _seed_collection(collection_name: str, seed_data: list):
    try:
        db = get_db()
        collection = db[collection_name]
        if collection.count_documents({}) == 0 and seed_data:
            collection.insert_many(seed_data)
            logging.info(f"Seeded {collection_name} with {len(seed_data)} records.")
    except Exception as e:
        logging.exception(f"Could not seed {collection_name}: {e}")


async def get_user_by_email(email: str) -> User | None:
    try:
        db = get_db()
        _seed_collection("users", SEED_USERS)
        return db.users.find_one({"email": email}, {"_id": 0})
    except Exception as e:
        logging.exception(f"Error fetching user: {e}")
        return None


async def create_user(user: User) -> bool:
    try:
        db = get_db()
        db.users.insert_one(user)
        return True
    except Exception as e:
        logging.exception(f"Error creating user: {e}")
        return False


async def get_all_cattle() -> list[Cattle]:
    try:
        db = get_db()
        cursor = db.cattle.find({}, {"_id": 0})
        return list(cursor)
    except Exception as e:
        logging.exception(f"Error fetching cattle: {e}")
        return []


async def create_cattle(cattle: Cattle) -> bool:
    try:
        db = get_db()
        db.cattle.insert_one(cattle)
        return True
    except Exception as e:
        logging.exception(f"Error creating cattle: {e}")
        return False


async def update_cattle(cattle_id: str, updates: dict) -> bool:
    try:
        db = get_db()
        result = db.cattle.update_one({"id": cattle_id}, {"$set": updates})
        return result.modified_count > 0
    except Exception as e:
        logging.exception(f"Error updating cattle: {e}")
        return False


async def get_all_crops() -> list[Crop]:
    try:
        db = get_db()
        cursor = db.crops.find({}, {"_id": 0})
        return list(cursor)
    except Exception as e:
        logging.exception(f"Error fetching crops: {e}")
        return []


async def create_crop(crop: Crop) -> bool:
    try:
        db = get_db()
        db.crops.insert_one(crop)
        return True
    except Exception as e:
        logging.exception(f"Error creating crop: {e}")
        return False


async def update_crop(crop_id: str, updates: dict) -> bool:
    try:
        db = get_db()
        result = db.crops.update_one({"id": crop_id}, {"$set": updates})
        return result.modified_count > 0
    except Exception as e:
        logging.exception(f"Error updating crop: {e}")
        return False


async def get_all_transactions() -> list[Transaction]:
    try:
        db = get_db()
        cursor = db.transactions.find({}, {"_id": 0})
        return list(cursor)
    except Exception as e:
        logging.exception(f"Error fetching transactions: {e}")
        return []


async def create_transaction(transaction: Transaction) -> bool:
    try:
        db = get_db()
        db.transactions.insert_one(transaction)
        return True
    except Exception as e:
        logging.exception(f"Error creating transaction: {e}")
        return False


async def get_all_coconut_sales() -> list[CoconutSale]:
    try:
        db = get_db()
        cursor = db.coconut_sales.find({}, {"_id": 0})
        return list(cursor)
    except Exception as e:
        logging.exception(f"Error fetching coconut sales: {e}")
        return []


async def create_coconut_sale(sale: CoconutSale) -> bool:
    try:
        db = get_db()
        db.coconut_sales.insert_one(sale)
        return True
    except Exception as e:
        logging.exception(f"Error creating coconut sale: {e}")
        return False


async def get_all_milk_sales() -> list[MilkSale]:
    try:
        db = get_db()
        cursor = db.milk_sales.find({}, {"_id": 0})
        return list(cursor)
    except Exception as e:
        logging.exception(f"Error fetching milk sales: {e}")
        return []


async def create_milk_sale(sale: MilkSale) -> bool:
    try:
        db = get_db()
        db.milk_sales.insert_one(sale)
        return True
    except Exception as e:
        logging.exception(f"Error creating milk sale: {e}")
        return False


async def get_all_breeding_cycles() -> list[BreedingCycle]:
    try:
        db = get_db()
        cursor = db.breeding_cycles.find({}, {"_id": 0})
        return list(cursor)
    except Exception as e:
        logging.exception(f"Error fetching breeding cycles: {e}")
        return []


async def create_breeding_cycle(cycle: BreedingCycle) -> bool:
    try:
        db = get_db()
        db.breeding_cycles.insert_one(cycle)
        return True
    except Exception as e:
        logging.exception(f"Error creating breeding cycle: {e}")
        return False


async def update_breeding_cycle(cycle_id: str, updates: dict) -> bool:
    try:
        db = get_db()
        result = db.breeding_cycles.update_one({"id": cycle_id}, {"$set": updates})
        return result.modified_count > 0
    except Exception as e:
        logging.exception(f"Error updating breeding cycle: {e}")
        return False


def init_database_seeds(seed_data_map: dict):
    """
    Initialize database with seed data if collections are empty.
    seed_data_map: dict where key is collection name and value is list of dicts
    """
    for collection_name, data in seed_data_map.items():
        if data:
            _seed_collection(collection_name, data)