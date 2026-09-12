import logging
import re
import uuid as _uuid
from datetime import datetime
from typing import Optional

from app.database.connection import get_db
from app.database.models import (
    ActivityLog,
    BreedingCycle,
    Cattle,
    CoconutSale,
    Crop,
    FamilyMember,
    Farm,
    FeedConsumption,
    FeedStock,
    FeedType,
    FeedingPlan,
    MilkSale,
    MilkSocietyRate,
    Transaction,
    User,
)

import time

logger = logging.getLogger(__name__)

_USER_CACHE: dict[str, tuple[float, User | None]] = {}
_SEEDED_FARMS: set[tuple[str, str]] = set()


def invalidate_user_cache(email: str) -> None:
    _USER_CACHE.pop(email.strip().lower(), None)


async def get_user_by_email(email: str) -> User | None:
    normalized_email = email.strip().lower()
    now = time.time()
    cached = _USER_CACHE.get(normalized_email)
    if cached and (now - cached[0] < 60):
        return cached[1]
    try:
        db = get_db()
        user = await db.users.find_one({"email": normalized_email}, {"_id": 0})
        _USER_CACHE[normalized_email] = (now, user)
        return user
    except Exception as e:
        logging.exception(f"Error fetching user: {e}")
        return None



async def get_farm(farm_id: str) -> Farm | None:
    """Fetch a farm's settings (name, location, size) by farm_id."""
    try:
        db = get_db()
        return await db.farms.find_one({"farm_id": farm_id}, {"_id": 0})
    except Exception as e:
        logging.exception(f"Error fetching farm: {e}")
        return None


async def upsert_farm(farm_id: str, settings: dict) -> bool:
    """Save (insert or replace) a farm's settings."""
    try:
        db = get_db()
        await db.farms.update_one(
            {"farm_id": farm_id},
            {"$set": {"farm_id": farm_id, **settings}},
            upsert=True,
        )
        return True
    except Exception as e:
        logging.exception(f"Error saving farm: {e}")
        return False


async def get_family_members(farm_id: str) -> list[FamilyMember]:
    """All family members who share access to a farm."""
    try:
        db = get_db()
        cursor = db.family_members.find({"farm_id": farm_id}, {"_id": 0})
        return await cursor.to_list(length=None)
    except Exception as e:
        logging.exception(f"Error fetching family members: {e}")
        return []


async def create_family_member(member: FamilyMember) -> bool:
    """Add a family member record to a farm."""
    try:
        db = get_db()
        await db.family_members.insert_one(_to_plain(member))
        return True
    except Exception as e:
        logging.exception(f"Error creating family member: {e}")
        return False


async def get_family_member_by_email(email: str) -> FamilyMember | None:
    """Find any family membership across farms for an email (used at sign-up)."""
    try:
        db = get_db()
        return await db.family_members.find_one({"email": email}, {"_id": 0})
    except Exception as e:
        logging.exception(f"Error fetching family member: {e}")
        return None


async def update_family_member_status(member_id: str, status: str) -> bool:
    """Mark a member active after they sign up."""
    try:
        db = get_db()
        result = await db.family_members.update_one(
            {"id": member_id}, {"$set": {"status": status}}
        )
        return result.modified_count > 0
    except Exception as e:
        logging.exception(f"Error updating family member: {e}")
        return False


async def delete_family_member(farm_id: str, member_id: str) -> bool:
    """Remove a family member from a farm (farm-scoped for safety)."""
    try:
        db = get_db()
        result = await db.family_members.delete_one({"id": member_id, "farm_id": farm_id})
        return result.deleted_count > 0
    except Exception as e:
        logging.exception(f"Error deleting family member: {e}")
        return False


async def update_user_farm_id(email: str, farm_id: str) -> bool:
    """Re-point an existing user at a farm (used to share/revoke farm access)."""
    try:
        db = get_db()
        result = await db.users.update_one(
            {"email": email}, {"$set": {"farm_id": farm_id}}
        )
        return result.modified_count > 0
    except Exception as e:
        logging.exception(f"Error updating user farm: {e}")
        return False


async def create_user(user: User) -> bool:
    try:
        db = get_db()
        await db.users.insert_one(_to_plain(user))
        return True
    except Exception as e:
        logging.exception(f"Error creating user: {e}")
        return False


async def get_all_cattle(farm_id: str) -> list[Cattle]:
    try:
        db = get_db()
        cursor = db.cattle.find({"farm_id": farm_id}, {"_id": 0})
        return await cursor.to_list(length=None)
    except Exception as e:
        logging.exception(f"Error fetching cattle: {e}")
        return []


async def create_cattle(cattle: Cattle) -> bool:
    try:
        db = get_db()
        await db.cattle.insert_one(_to_plain(cattle))
        return True
    except Exception as e:
        logging.exception(f"Error creating cattle: {e}")
        return False


async def update_user_profile(
    email: str, name: Optional[str] = None, phone: Optional[str] = None
) -> bool:
    """Update a user's name and/or phone number."""
    try:
        db = get_db()
        updates = {}
        if name is not None:
            updates["name"] = name
        if phone is not None:
            updates["phone"] = phone
        if not updates:
            return True
        result = await db.users.update_one({"email": email}, {"$set": updates})
        return result.matched_count > 0 or result.modified_count > 0
    except Exception as e:
        logging.exception(f"Error updating user profile: {e}")
        return False


async def update_cattle(
    cattle_id: str, updates: dict, farm_id: Optional[str] = None
) -> bool:
    try:
        db = get_db()
        query = {"id": cattle_id}
        if farm_id:
            query["farm_id"] = farm_id
        result = await db.cattle.update_one(query, {"$set": _to_plain(updates)})
        return result.matched_count > 0 or result.modified_count > 0
    except Exception as e:
        logging.exception(f"Error updating cattle: {e}")
        return False


async def get_all_crops(farm_id: str) -> list[Crop]:
    try:
        db = get_db()
        cursor = db.crops.find({"farm_id": farm_id}, {"_id": 0})
        return await cursor.to_list(length=None)
    except Exception as e:
        logging.exception(f"Error fetching crops: {e}")
        return []


async def create_crop(crop: Crop) -> bool:
    try:
        db = get_db()
        await db.crops.insert_one(_to_plain(crop))
        return True
    except Exception as e:
        logging.exception(f"Error creating crop: {e}")
        return False


async def update_crop(
    crop_id: str, updates: dict, farm_id: Optional[str] = None
) -> bool:
    try:
        db = get_db()
        query = {"id": crop_id}
        if farm_id:
            query["farm_id"] = farm_id
        result = await db.crops.update_one(query, {"$set": _to_plain(updates)})
        return result.matched_count > 0 or result.modified_count > 0
    except Exception as e:
        logging.exception(f"Error updating crop: {e}")
        return False


async def get_all_transactions(farm_id: str) -> list[Transaction]:
    try:
        db = get_db()
        cursor = db.transactions.find({"farm_id": farm_id}, {"_id": 0})
        return await cursor.to_list(length=None)
    except Exception as e:
        logging.exception(f"Error fetching transactions: {e}")
        return []


async def create_transaction(transaction: Transaction) -> bool:
    try:
        db = get_db()
        await db.transactions.insert_one(_to_plain(transaction))
        return True
    except Exception as e:
        logging.exception(f"Error creating transaction: {e}")
        return False


async def delete_transactions_by_note(farm_id: str, note_prefix: str) -> int:
    """Delete transactions whose notes start with a prefix (used to unlink a
    milk sale from its auto-created income transaction when the bill is deleted)."""
    try:
        db = get_db()
        result = await db.transactions.delete_many(
            {
                "farm_id": farm_id,
                "notes": {"$regex": f"^{re.escape(note_prefix)}"},
            }
        )
        return result.deleted_count
    except Exception as e:
        logging.exception(f"Error deleting transactions by note: {e}")
        return 0


async def get_all_coconut_sales(farm_id: str) -> list[CoconutSale]:
    try:
        db = get_db()
        cursor = db.coconut_sales.find({"farm_id": farm_id}, {"_id": 0})
        return await cursor.to_list(length=None)
    except Exception as e:
        logging.exception(f"Error fetching coconut sales: {e}")
        return []


async def create_coconut_sale(sale: CoconutSale) -> bool:
    try:
        db = get_db()
        await db.coconut_sales.insert_one(_to_plain(sale))
        return True
    except Exception as e:
        logging.exception(f"Error creating coconut sale: {e}")
        return False


async def get_all_milk_sales(farm_id: str) -> list[MilkSale]:
    try:
        db = get_db()
        cursor = db.milk_sales.find({"farm_id": farm_id}, {"_id": 0})
        return await cursor.to_list(length=None)
    except Exception as e:
        logging.exception(f"Error fetching milk sales: {e}")
        return []


async def create_milk_sale(sale: MilkSale) -> bool:
    try:
        db = get_db()
        await db.milk_sales.insert_one(_to_plain(sale))
        return True
    except Exception as e:
        logging.exception(f"Error creating milk sale: {e}")
        return False


async def update_milk_sale(
    sale_id: str, updates: dict, farm_id: Optional[str] = None
) -> bool:
    """Update fields on a single milk sale (e.g. payment status)."""
    try:
        db = get_db()
        query = {"id": sale_id}
        if farm_id:
            query["farm_id"] = farm_id
        result = await db.milk_sales.update_one(query, {"$set": _to_plain(updates)})
        return result.matched_count > 0 or result.modified_count > 0
    except Exception as e:
        logging.exception(f"Error updating milk sale: {e}")
        return False


async def delete_milk_sale(sale_id: str, farm_id: Optional[str] = None) -> bool:
    """Delete a milk sale by id (farm-scoped for safety)."""
    try:
        db = get_db()
        query = {"id": sale_id}
        if farm_id:
            query["farm_id"] = farm_id
        result = await db.milk_sales.delete_one(query)
        return result.deleted_count > 0
    except Exception as e:
        logging.exception(f"Error deleting milk sale: {e}")
        return False


async def get_milk_rate_table(farm_id: str, society: str) -> MilkSocietyRate | None:
    """Fetch the fat%-slab rate table for one society."""
    try:
        db = get_db()
        return await db.milk_rate_tables.find_one(
            {"farm_id": farm_id, "society": society}, {"_id": 0}
        )
    except Exception as e:
        logging.exception(f"Error fetching milk rate table: {e}")
        return None


async def upsert_milk_rate_table(
    farm_id: str, society: str, slabs: list[dict]
) -> bool:
    """Save (insert or replace) the rate slab table for a society."""
    try:
        db = get_db()
        clean_slabs = [
            {"fat_min": float(s["fat_min"]), "rate": float(s["rate"])}
            for s in slabs
            if float(s.get("fat_min", 0) or 0) > 0 and float(s.get("rate", 0) or 0) >= 0
        ]
        clean_slabs.sort(key=lambda s: s["fat_min"])
        await db.milk_rate_tables.update_one(
            {"farm_id": farm_id, "society": society},
            {"$set": {"farm_id": farm_id, "society": society, "slabs": clean_slabs}},
            upsert=True,
        )
        return True
    except Exception as e:
        logging.exception(f"Error saving milk rate table: {e}")
        return False


async def get_all_breeding_cycles(farm_id: str) -> list[BreedingCycle]:
    try:
        db = get_db()
        cursor = db.breeding_cycles.find({"farm_id": farm_id}, {"_id": 0})
        return await cursor.to_list(length=None)
    except Exception as e:
        logging.exception(f"Error fetching breeding cycles: {e}")
        return []


async def create_breeding_cycle(cycle: BreedingCycle) -> bool:
    try:
        db = get_db()
        await db.breeding_cycles.insert_one(_to_plain(cycle))
        return True
    except Exception as e:
        logging.exception(f"Error creating breeding cycle: {e}")
        return False


async def update_breeding_cycle(
    cycle_id: str, updates: dict, farm_id: Optional[str] = None
) -> bool:
    try:
        db = get_db()
        query = {"id": cycle_id}
        if farm_id:
            query["farm_id"] = farm_id
        result = await db.breeding_cycles.update_one(
            query, {"$set": _to_plain(updates)}
        )
        return result.matched_count > 0 or result.modified_count > 0
    except Exception as e:
        logging.exception(f"Error updating breeding cycle: {e}")
        return False


async def get_feed_types(farm_id: str) -> list[FeedType]:
    try:
        db = get_db()
        cursor = db.feed_types.find({"farm_id": farm_id}, {"_id": 0})
        return await cursor.to_list(length=None)
    except Exception as e:
        logging.exception(f"Error fetching feed types: {e}")
        return []


async def create_feed_type(feed_type: FeedType) -> bool:
    try:
        db = get_db()
        await db.feed_types.insert_one(_to_plain(feed_type))
        return True
    except Exception as e:
        logging.exception(f"Error creating feed type: {e}")
        return False


async def get_feed_stock(farm_id: str) -> list[FeedStock]:
    try:
        db = get_db()
        cursor = db.feed_stock.find({"farm_id": farm_id}, {"_id": 0})
        return await cursor.to_list(length=None)
    except Exception as e:
        logging.exception(f"Error fetching feed stock: {e}")
        return []


async def create_feed_stock(stock: FeedStock) -> bool:
    try:
        db = get_db()
        await db.feed_stock.insert_one(_to_plain(stock))
        return True
    except Exception as e:
        logging.exception(f"Error creating feed stock: {e}")
        return False


async def update_feed_stock(
    stock_id: str, updates: dict, farm_id: Optional[str] = None
) -> bool:
    try:
        db = get_db()
        query = {"id": stock_id}
        if farm_id:
            query["farm_id"] = farm_id
        result = await db.feed_stock.update_one(query, {"$set": _to_plain(updates)})
        return result.matched_count > 0 or result.modified_count > 0
    except Exception as e:
        logging.exception(f"Error updating feed stock: {e}")
        return False


async def get_feed_consumptions(farm_id: str) -> list[FeedConsumption]:
    try:
        db = get_db()
        cursor = db.feed_consumptions.find({"farm_id": farm_id}, {"_id": 0})
        return await cursor.to_list(length=None)
    except Exception as e:
        logging.exception(f"Error fetching feed consumptions: {e}")
        return []


async def create_feed_consumption(consumption: FeedConsumption) -> bool:
    try:
        db = get_db()
        await db.feed_consumptions.insert_one(_to_plain(consumption))
        return True
    except Exception as e:
        logging.exception(f"Error creating feed consumption: {e}")
        return False


async def get_feeding_plans(farm_id: str) -> list[FeedingPlan]:
    try:
        db = get_db()
        cursor = db.feeding_plans.find({"farm_id": farm_id}, {"_id": 0})
        return await cursor.to_list(length=None)
    except Exception as e:
        logging.exception(f"Error fetching feeding plans: {e}")
        return []


async def create_feeding_plan(plan: FeedingPlan) -> bool:
    try:
        db = get_db()
        await db.feeding_plans.insert_one(_to_plain(plan))
        return True
    except Exception as e:
        logging.exception(f"Error creating feeding plan: {e}")
        return False


async def get_feed_sync_markers(farm_id: str) -> dict[str, float]:
    """All crop-to-feed-stock sync markers for a farm (crop_id -> moved qty)."""
    try:
        db = get_db()
        cursor = db.feed_sync_markers.find(
            {"farm_id": farm_id}, {"_id": 0, "key": 1, "value": 1}
        )
        markers: dict[str, float] = {}
        async for doc in cursor:
            try:
                markers[doc["key"]] = float(doc["value"])
            except (KeyError, TypeError, ValueError):
                continue
        return markers
    except Exception as e:
        logging.exception(f"Error fetching feed sync markers: {e}")
        return {}


async def set_feed_sync_marker(farm_id: str, key: str, value: str) -> bool:
    """Record how much of a crop's harvest has been moved into feed stock."""
    try:
        db = get_db()
        await db.feed_sync_markers.update_one(
            {"farm_id": farm_id, "key": key},
            {"$set": {"farm_id": farm_id, "key": key, "value": value}},
            upsert=True,
        )
        return True
    except Exception as e:
        logging.exception(f"Error setting feed sync marker: {e}")
        return False


async def log_activity(
    user_email: str,
    action: str,
    entity_type: str,
    entity_id: Optional[str] = None,
    details: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> bool:
    """Log a user activity to the database."""
    try:
        import uuid as _uuid

        db = get_db()
        log_entry: ActivityLog = {
            "id": str(_uuid.uuid4()),
            "user_email": user_email,
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "ip_address": ip_address,
        }
        await db.activity_logs.insert_one(_to_plain(log_entry))
        return True
    except Exception as e:
        logging.exception(f"Error logging activity: {e}")
        return False


def _to_plain(obj):
    """Recursively convert Reflex state proxies into plain dict/list scalars.

    Reflex wraps mutable state values (lists of dicts) in MutableProxy objects
    that MongoDB's BSON encoder cannot serialize. Converting here makes seeding
    safe no matter what the caller passes in.
    """
    if isinstance(obj, dict):
        return {str(k): _to_plain(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_plain(v) for v in obj]
    return obj


async def ensure_farm_seed(collection_name: str, farm_id: str, seed_data: list) -> None:
    """Insert demo rows for a farm if that farm has no rows in the collection yet.

    Each seeded row gets the farm's real farm_id and a freshly generated id so
    demo ids never collide across farms (updates are id-based).
    """
    if not farm_id or (collection_name, farm_id) in _SEEDED_FARMS:
        return
    try:
        db = get_db()
        collection = db[collection_name]
        # Fast indexed lookup instead of counting the entire collection
        existing = await collection.find_one({"farm_id": farm_id}, {"_id": 1})
        if existing is not None or not seed_data:
            _SEEDED_FARMS.add((collection_name, farm_id))
            return
        rows = [
            _to_plain({**item, "id": str(_uuid.uuid4()), "farm_id": farm_id})
            for item in seed_data
        ]
        await collection.insert_many(rows)
        _SEEDED_FARMS.add((collection_name, farm_id))
        logging.info(
            f"Seeded {collection_name} for farm {farm_id} with {len(rows)} records."
        )
    except Exception as e:
        logging.exception(f"Could not seed {collection_name} for farm {farm_id}: {e}")

