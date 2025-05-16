import hashlib
from typing import Union

from sqlalchemy import select

from services.backend.modules.auth.schemas import User
from services.backend.modules.base import ModuleWithDb

from services.db.models import ApiKey


class AuthModule(ModuleWithDb):
    async def get_current_user(self, api_key: str) -> Union[User, None]:
        query = (
            select(ApiKey)
            .where(
                ApiKey.api_key == self.hash_api_key(api_key)
            )
        )
        async with self.db.session_scope() as sess:
            user = await sess.execute(query)
            user = user.scalar_one_or_none()
            if user:
                result = User(id=user.user_id)
            else:
                result = None
        return result

    @staticmethod
    def hash_api_key(api_key: str) -> str:
        return hashlib.sha256(api_key.encode()).hexdigest()
