from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.api_key import ApiKey


class ApiKeyService:

    def __init__(self, session: AsyncSession):
        self._db = session

    async def create(self, api_key: ApiKey) -> ApiKey:
        """
        Create a new API key in database.

        :param api_key: The API key to create.
        :return: None
        """

        db_api_key = ApiKey(**api_key.model_dump())
        self._db.add(db_api_key)
        await self._db.commit()
        await self._db.refresh(db_api_key)
        logger.info("Created API key: {}", db_api_key.id)

        return db_api_key
