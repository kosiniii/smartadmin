from sqlalchemy.ext.asyncio import AsyncSession

class PRU:
    def __init__(self, option: str, db_session: AsyncSession):
        self.option = option
        self.db_session = db_session
    
    def procent_mat(self):
        pass
    