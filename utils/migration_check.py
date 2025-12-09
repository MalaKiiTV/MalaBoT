"""Database migration verification utility"""

import asyncio
import logging
from database.supabase_models import DatabaseManager

logger = logging.getLogger(__name__)


async def verify_migrations():
    """Verify Supabase connection and basic functionality"""
    try:
        db = DatabaseManager()
        await db.initialize()

        # Test basic database connectivity
        try:
            # Try a simple query to verify connection
            result = db.supabase.table('users').select('count').execute()
            logger.info("Supabase connection verified ✅")
            return True
        except Exception as e:
            logger.error(f"Supabase connection failed: {e}")
            return False

    except Exception as e:
        logger.error(f"Database verification failed: {e}")
        return False
    finally:
        # Supabase doesn't need explicit connection closing
        pass


if __name__ == "__main__":
    asyncio.run(verify_migrations())