from typing import Annotated, List, Union

from fastapi import APIRouter, Depends

from services.backend import Backend, get_backend
from services.backend.modules.organization.schemas import OrgFull

router = APIRouter(prefix='/org', tags=['org'])


@router.get('/coords',
            summary='Get organizations by coords',
            response_model=List[OrgFull])
async def get_by_coords(
        backend: Annotated[Backend, Depends(get_backend)],
        lon: float,
        lat: float
):
    return await backend.org_module.get_by_coords(lon=lon, lat=lat)

@router.get('/id',
            summary='Get organization by id',
            response_model=Union[OrgFull, None])
async def get_by_id(
        backend: Annotated[Backend, Depends(get_backend)],
        org_id: int
):
    return await backend.org_module.get_by_id(org_id=org_id)

@router.get('/category',
            summary='Get organizations by category tree',
            response_model=List[OrgFull])
async def get_by_categories(
        backend: Annotated[Backend, Depends(get_backend)],
        cat_id: int
):
    categories = await backend.cat_module.get_tree(cat_id=cat_id)
    return await backend.org_module.get_by_categories(cat_ids=[x.id for x in categories])

@router.get('/name',
            summary='Get organizations by name. "%" wildcard is supported.',
            response_model=List[OrgFull])
async def get_by_name(
        backend: Annotated[Backend, Depends(get_backend)],
        name: str
):
    return await backend.org_module.get_by_name(name=name)

@router.get('/radius',
            summary='Get organizations inside radius',
            response_model=List[OrgFull])
async def get_by_radius(
        backend: Annotated[Backend, Depends(get_backend)],
        lon: float,
        lat: float,
        radius_meters: int
):
    return await backend.org_module.get_by_radius(lon=lon, lat=lat, radius_meters=radius_meters)

@router.get('/area',
            summary='Get organizations inside area. The parameters are the coordinates of the center and the width and height of the area, measured in meters.',
            response_model=List[OrgFull])
async def get_by_area(
        backend: Annotated[Backend, Depends(get_backend)],
        lon: float,
        lat: float,
        height: int,
        width: int
):
    return await backend.org_module.get_by_area(lon=lon, lat=lat, height=height, width=width)
