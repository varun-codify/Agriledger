"""Database indexing configuration for MongoDB.

Every query in this app is farm-scoped, so all hot paths get a
``farm_id``-leading compound index instead of relying on single-field
indexes that only partially cover the filter.
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

        # Farms collection
        await db.farms.create_index("farm_id", unique=True)
        logger.info("Created index: farms.farm_id (unique)")

        # Family members collection
        await db.family_members.create_index("farm_id")
        await db.family_members.create_index("email")
        logger.info("Created indexes: family_members.farm_id, email")

        # Cattle collection
        await db.cattle.create_index([("farm_id", 1), ("animal_type", 1)])
        await db.cattle.create_index([("farm_id", 1), ("health_status", 1)])
        await db.cattle.create_index([("farm_id", 1), ("is_active", 1)])
        logger.info("Created indexes: cattle (farm_id, animal_type/health_status/is_active)")

        # Crops collection
        await db.crops.create_index([("farm_id", 1), ("status", 1)])
        await db.crops.create_index([("farm_id", 1), ("planting_date", 1)])
        logger.info("Created indexes: crops (farm_id, status/planting_date)")

        # Transactions collection
        await db.transactions.create_index([("farm_id", 1), ("date", -1)])
        await db.transactions.create_index([("farm_id", 1), ("type", 1)])
        await db.transactions.create_index([("farm_id", 1), ("category.name", 1)])
        logger.info("Created indexes: transactions (farm_id, date/type/category.name)")

        # Coconut sales collection
        await db.coconut_sales.create_index([("farm_id", 1), ("date", -1)])
        await db.coconut_sales.create_index([("farm_id", 1), ("buyer", 1)])
        logger.info("Created indexes: coconut_sales (farm_id, date/buyer)")

        # Milk sales collection
        await db.milk_sales.create_index([("farm_id", 1), ("date", -1)])
        await db.milk_sales.create_index([("farm_id", 1), ("animal_id", 1)])
        await db.milk_sales.create_index([("farm_id", 1), ("buyer", 1)])
        await db.milk_sales.create_index([("farm_id", 1), ("payment_status", 1)])
        await db.milk_rate_tables.create_index([("farm_id", 1), ("society", 1)])
        logger.info(
            "Created indexes: milk_sales (farm_id, date/animal_id/buyer/payment_status); milk_rate_tables (farm_id, society)"
        )

        # Breeding cycles collection
        await db.breeding_cycles.create_index([("farm_id", 1), ("cattle_id", 1)])
        await db.breeding_cycles.create_index([("farm_id", 1), ("status", 1)])
        await db.breeding_cycles.create_index(
            [("farm_id", 1), ("insemination_date", 1)]
        )
        await db.breeding_cycles.create_index(
            [("farm_id", 1), ("expected_calving_date", 1)]
        )
        logger.info("Created indexes: breeding_cycles (farm_id, cattle_id/status/dates)")

        # Feed collections
        await db.feed_types.create_index([("farm_id", 1)])
        await db.feed_stock.create_index([("farm_id", 1), ("feed_type_id", 1)])
        await db.feed_consumptions.create_index([("farm_id", 1), ("date", -1)])
        await db.feed_consumptions.create_index([("farm_id", 1), ("animal_id", 1)])
        await db.feeding_plans.create_index([("farm_id", 1), ("category", 1)])
        await db.feed_sync_markers.create_index([("farm_id", 1), ("key", 1)])
        logger.info(
            "Created indexes: feed_types, feed_stock, feed_consumptions, feeding_plans, feed_sync_markers"
        )

        # Activity logs collection (not farm-scoped: keyed by user_email)
        await db.activity_logs.create_index("user_email")
        await db.activity_logs.create_index("timestamp")
        await db.activity_logs.create_index("entity_type")
        logger.info("Created indexes: activity_logs.user_email, timestamp, entity_type")

        logger.info("All database indexes created successfully.")
    except Exception as e:
        logger.exception(f"Error creating database indexes: {e}")
        raise
