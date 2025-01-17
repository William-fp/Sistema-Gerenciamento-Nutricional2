from fastapi import APIRouter

router = APIRouter(
    prefix="",  
    tags=["Home"],  
)


@router.get("/")
async def root():
    return {"message": "API do sistema de Informação nutricional"}