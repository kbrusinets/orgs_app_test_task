from typing import List, Union

from geoalchemy2 import Geography, Geometry
from geoalchemy2 import functions as geo_func
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import Point
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from services.backend.modules.base import ModuleWithDb
from services.backend.modules.category.schemas import CategoryFull
from services.backend.modules.organization.schemas import OrgFull
from services.db.models import Address, Category, Organization


class OrganizationModule(ModuleWithDb):
    async def get_by_id(self, org_id: int) -> Union[OrgFull, None]:
        query = (
            select(Organization)
            .options(
                selectinload(Organization.address),
                selectinload(Organization.categories),
            )
            .where(Organization.id == org_id)
        )
        async with self.db.session_scope() as sess:
            org = await sess.execute(query)
            org = org.scalar_one_or_none()
            if org:
                org_coords = to_shape(org.address.coordinates)
                result = OrgFull(
                    id=org.id,
                    name=org.name,
                    coordinates=f"{org_coords.y}, {org_coords.x}",
                    address=f"{org.address.country}, {org.address.city}, {org.address.street}, {org.address.home}",
                    categories=[
                        CategoryFull(id=cat.id, parent_id=cat.parent_id, name=cat.name)
                        for cat in org.categories
                    ],
                )
            else:
                result = None
        return result

    async def get_by_coords(self, lon: float, lat: float) -> List[OrgFull]:
        query = (
            select(Address)
            .options(
                selectinload(Address.organizations).selectinload(
                    Organization.categories
                )
            )
            .where(Address.coordinates == from_shape(Point(lon, lat), srid=4326))
        )
        result = []
        async with self.db.session_scope() as sess:
            address = await sess.execute(query)
            address = address.scalar_one_or_none()
            organizations = address.organizations if address else []
            for organization in organizations:
                org_coords = to_shape(address.coordinates)
                result.append(
                    OrgFull(
                        id=organization.id,
                        name=organization.name,
                        coordinates=f"{org_coords.y}, {org_coords.x}",
                        address=f"{address.country}, {address.city}, {address.street}, {address.home}",
                        categories=[
                            CategoryFull(
                                id=cat.id, parent_id=cat.parent_id, name=cat.name
                            )
                            for cat in organization.categories
                        ],
                    )
                )
            sess.expunge_all()
        return result

    async def get_by_categories(self, cat_ids: List[int]) -> List[OrgFull]:
        query = (
            select(Category)
            .options(
                selectinload(Category.organizations).selectinload(
                    Organization.categories
                ),
                selectinload(Category.organizations).selectinload(Organization.address),
            )
            .where(Category.id.in_(cat_ids))
        )
        result = []
        result_ids = set()
        async with self.db.session_scope() as sess:
            res = await sess.execute(query)
            categories: List[Category] = res.scalars().all()
            for cat in categories:
                for org in cat.organizations:
                    if org.id not in result_ids:
                        org_coords = to_shape(org.address.coordinates)
                        result.append(
                            OrgFull(
                                id=org.id,
                                name=org.name,
                                coordinates=f"{org_coords.y}, {org_coords.x}",
                                address=f"{org.address.country}, {org.address.city}, {org.address.street}, {org.address.home}",
                                categories=[
                                    CategoryFull(
                                        id=cat.id,
                                        parent_id=cat.parent_id,
                                        name=cat.name,
                                    )
                                    for cat in org.categories
                                ],
                            )
                        )
                        result_ids.add(org.id)
            sess.expunge_all()
        return result

    async def get_by_name(self, name: str) -> List[OrgFull]:
        query = (
            select(Organization)
            .options(
                selectinload(Organization.categories),
                selectinload(Organization.address),
            )
            .where(Organization.name.ilike(name))
        )
        result = []
        result_ids = set()
        async with self.db.session_scope() as sess:
            res = await sess.execute(query)
            organizations: List[Organization] = res.scalars().all()
            for org in organizations:
                if org.id not in result_ids:
                    org_coords = to_shape(org.address.coordinates)
                    result.append(
                        OrgFull(
                            id=org.id,
                            name=org.name,
                            coordinates=f"{org_coords.y}, {org_coords.x}",
                            address=f"{org.address.country}, {org.address.city}, {org.address.street}, {org.address.home}",
                            categories=[
                                CategoryFull(
                                    id=cat.id, parent_id=cat.parent_id, name=cat.name
                                )
                                for cat in org.categories
                            ],
                        )
                    )
                    result_ids.add(org.id)
            sess.expunge_all()
        return result

    async def get_by_radius(self, lon: float, lat: float, radius_meters: int):
        query = (
            select(Address)
            .options(
                selectinload(Address.organizations).selectinload(
                    Organization.categories
                )
            )
            .where(
                geo_func.ST_DWithin(
                    Address.coordinates,
                    geo_func.ST_SetSRID(geo_func.ST_Point(lon, lat), 4326),
                    radius_meters,
                )
            )
        )
        result = []
        result_ids = set()
        async with self.db.session_scope() as sess:
            res = await sess.execute(query)
            addresses: List[Address] = res.scalars().all()
            for addr in addresses:
                for org in addr.organizations:
                    if org.id not in result_ids:
                        org_coords = to_shape(addr.coordinates)
                        result.append(
                            OrgFull(
                                id=org.id,
                                name=org.name,
                                coordinates=f"{org_coords.y}, {org_coords.x}",
                                address=f"{addr.country}, {addr.city}, {addr.street}, {addr.home}",
                                categories=[
                                    CategoryFull(
                                        id=cat.id,
                                        parent_id=cat.parent_id,
                                        name=cat.name,
                                    )
                                    for cat in org.categories
                                ],
                            )
                        )
                        result_ids.add(org.id)
        return result

    async def get_by_area(self, lon: float, lat: float, height: int, width: int):
        center = select(
            geo_func.ST_SetSRID(geo_func.ST_MakePoint(lon, lat), 4326)
            .cast(Geography)
            .label("geom")
        ).cte("center")

        ns = select(
            geo_func.ST_Project(center.c.geom, height / 2, func.radians(0)).label(
                "north"
            ),
            geo_func.ST_Project(center.c.geom, height / 2, func.radians(180)).label(
                "south"
            ),
        ).cte("ns")

        corners = select(
            geo_func.ST_Project(ns.c.north, width / 2, func.radians(90)).label("ne"),
            geo_func.ST_Project(ns.c.south, width / 2, func.radians(270)).label("sw"),
        ).cte("corners")

        rectangle = select(
            geo_func.ST_MakeEnvelope(
                geo_func.ST_X(func.cast(corners.c.sw, Geometry)),
                geo_func.ST_Y(func.cast(corners.c.sw, Geometry)),
                geo_func.ST_X(func.cast(corners.c.ne, Geometry)),
                geo_func.ST_Y(func.cast(corners.c.ne, Geometry)),
                4326,
            ).label("rect")
        ).cte("rectangle")

        query = (
            select(Address)
            .options(
                selectinload(Address.organizations).selectinload(
                    Organization.categories
                )
            )
            .where(
                geo_func.ST_Intersects(
                    Address.coordinates, func.cast(rectangle.c.rect, Geography)
                )
            )
        )

        result = []
        result_ids = set()
        async with self.db.session_scope() as sess:
            res = await sess.execute(query)
            addresses: List[Address] = res.scalars().all()
            for addr in addresses:
                for org in addr.organizations:
                    if org.id not in result_ids:
                        org_coords = to_shape(addr.coordinates)
                        result.append(
                            OrgFull(
                                id=org.id,
                                name=org.name,
                                coordinates=f"{org_coords.y}, {org_coords.x}",
                                address=f"{addr.country}, {addr.city}, {addr.street}, {addr.home}",
                                categories=[
                                    CategoryFull(
                                        id=cat.id,
                                        parent_id=cat.parent_id,
                                        name=cat.name,
                                    )
                                    for cat in org.categories
                                ],
                            )
                        )
                        result_ids.add(org.id)
        return result
