from functools import lru_cache

from services.backend.modules.category.module import CategoryModule
from services.backend.modules.organization.module import OrganizationModule
from services.db import Db, get_db


class Backend:
    def __init__(self, db: Db):
        self.org_module = OrganizationModule(db=db)
        self.cat_module = CategoryModule(db=db)


@lru_cache
def get_backend() -> Backend:
    return Backend(get_db())
