from sqlalchemy.ext.asyncio import AsyncSession



class DataService:

    def __init__(self, session: AsyncSession):
        self._db = session

    async def create(self):
        pass