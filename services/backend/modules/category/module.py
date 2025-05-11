from typing import List
from sqlalchemy import select

from services.backend.modules.base import ModuleWithDb

from services.backend.modules.category.schemas import CategoryFull
from services.db.models import Category


class CategoryModule(ModuleWithDb):
    async def get_tree(self, cat_id) -> List[CategoryFull]:
        query = (
            select(Category)
            .where(
                Category.id == cat_id
            )
        )
        result = []
        result_ids = set()
        cur_cats = []
        async with self.db.session_scope() as sess:
            category = await sess.execute(query)
            category = category.scalar_one_or_none()
            if category:
                result.append(CategoryFull(
                    id=category.id,
                    parent_id=category.parent_id,
                    name=category.name
                ))
                cur_cats.append(category.id)
                result_ids.add(category.id)
            while cur_cats:
                query = (
                    select(Category)
                    .where(
                        Category.parent_id.in_(cur_cats)
                    )
                )
                categories = await sess.execute(query)
                categories = categories.scalars().all()
                cur_cats = []
                for cat in categories:
                    if cat.id not in result_ids:
                        result.append(CategoryFull(
                            id=cat.id,
                            parent_id=cat.parent_id,
                            name=cat.name
                        ))
                        cur_cats.append(cat.id)
                        result_ids.add(cat.id)
        return result
