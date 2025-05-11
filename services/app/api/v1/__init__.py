from fastapi import APIRouter

from .organization import router as org_router

router = APIRouter(prefix='/v1')
router.include_router(org_router)
