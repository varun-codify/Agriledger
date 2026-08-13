"""Database indexing configuration for MongoDB.

Creates indexes on frequently queried collections to improve performance.
Index creation is asynchronous (Motor) and safe to call at startup.
"""

import logging

logger = logging.getLogger(__name__)


async def create_indexes(db) -> None:
    """Create all database indexes for performance optimization.

    This should be called once at application startup.
    """
    try:
        # Users collection
        await db.users.create_index("email", unique=True)
        logger.info("Created index: users.email (unique)")

        # Cattle collection
        await db.cattle.create_index("animal_type")
        await db.cattle.create_index("health_status")
        await db.cattle.create_index("is_active")
        logger.info("Created indexes: cattle.animal_type, health_status, is_active")

        # Crops collection
        await db.crops.create_index("status")
        await db.crops.create_index("planting_date")
        logger.info("Created indexes: crops.status, planting_date")

        # Transactions collection
        await db.transactions.create_index("type")
        await db.transactions.create_index("date")
        await db.transactions.create_index("category.name")
        logger.info("Created indexes: transactions.type, date, category.name")

        # Coconut sales collection
        await db.coconut_sales.create_index("date")
        await db.coconut_sales.create_index("buyer")
        logger.info("Created indexes: coconut_sales.date, buyer")

        # Milk sales collection
        await db.milk_sales.create_index("date")
        await db.milk_sales.create_index("animal_id")
        await db.milk_sales.create_index("buyer")
        await db.milk_sales.create_index("payment_status")
        await db.milk_rate_tables.create_index("society")
        logger.info(
            "Created indexes: milk_sales.date, animal_id, buyer, payment_status; milk_rate_tables.society"
        )

        # Breeding cycles collection
        await db.breeding_cycles.create_index("cattle_id")
        await db.breeding_cycles.create_index("status")
        await db.breeding_cycles.create_index("insemination_date")
        await db.breeding_cycles.create_index("expected_calving_date")
        logger.info("Created indexes: breeding_cycles.cattle_id, status, dates")

        # Feed collections
        await db.feed_types.create_index("farm_id")
        await db.feed_stock.create_index("farm_id")
        await db.feed_stock.create_index("feed_type_id")
        await db.feed_consumptions.create_index("farm_id")
        await db.feed_consumptions.create_index("date")
        await db.feed_consumptions.create_index("animal_id")
        await db.feeding_plans.create_index("farm_id")
        await db.feeding_plans.create_index("category")
        await db.feed_sync_markers.create_index("farm_id")
        logger.info(
            "Created indexes: feed_types, feed_stock, feed_consumptions, feeding_plans, feed_sync_markers"
        )

        # Activity logs collection
        await db.activity_logs.create_index("user_email")
        await db.activity_logs.create_index("timestamp")
        await db.activity_logs.create_index("entity_type")
        logger.info("Created indexes: activity_logs.user_email, timestamp, entity_type")

        logger.info("All database indexes created successfully.")
    except Exception as e:
        logger.exception(f"Error creating database indexes: {e}")
