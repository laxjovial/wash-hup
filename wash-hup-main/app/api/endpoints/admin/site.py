from fastapi import APIRouter, status, HTTPException, Body
from ...dependencies import admin_dependency, db_dependency, get_profile_model
from app.models.admin.profile import Faqs, TermsAndConditions, Category
from app.schemas.request.admin import FAQCreateSchema, FAQUpdateSchema, TermsCreateSchema
from app.schemas.response.admin import AdminBaseResponse, AdminDataResponse
from uuid import uuid4
from datetime import datetime
from typing import Optional


router = APIRouter(
    prefix="/site",
    tags=["Admin: Site Content"]
)

@router.get("/faqs", status_code=status.HTTP_200_OK, response_model=AdminDataResponse)
async def get_faqs(db: db_dependency, admin: admin_dependency, category: Optional[Category] = None):
    query = db.query(Faqs)
    if category:
        query = query.filter(Faqs.category == category)
    faqs = query.all()
    return {"status": "success", "data": faqs}

@router.post("/faqs", status_code=status.HTTP_201_CREATED, response_model=AdminDataResponse)
async def create_faq(
    db: db_dependency,
    admin: admin_dependency,
    data: FAQCreateSchema
):
    profile = get_profile_model(db, admin.get("id"))
    faq = Faqs(
        id="faq_"+str(uuid4()),
        admin_id=profile.id,
        category=data.category,
        question=data.question,
        answer=data.answer
    )
    db.add(faq)
    db.commit()
    db.refresh(faq)
    return {"status": "success", "data": faq}

@router.put("/faqs/{faq_id}", status_code=status.HTTP_200_OK, response_model=AdminDataResponse)
async def update_faq(
    faq_id: str,
    db: db_dependency,
    admin: admin_dependency,
    data: FAQUpdateSchema
):
    faq = db.query(Faqs).filter(Faqs.id == faq_id).first()
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")

    if data.question: faq.question = data.question
    if data.answer: faq.answer = data.answer

    db.commit()
    db.refresh(faq)
    return {"status": "success", "data": faq}

@router.get("/terms", status_code=status.HTTP_200_OK)
async def get_terms(db: db_dependency, admin: admin_dependency, category: Optional[Category] = None):
    query = db.query(TermsAndConditions)
    if category:
        query = query.filter(TermsAndConditions.category == category)
    terms = query.all()
    return {"status": "success", "data": terms}

@router.post("/terms", status_code=status.HTTP_201_CREATED, response_model=AdminDataResponse)
async def create_terms(
    db: db_dependency,
    admin: admin_dependency,
    data: TermsCreateSchema
):
    profile = get_profile_model(db, admin.get("id"))
    term = TermsAndConditions(
        id="term_"+str(uuid4()),
        admin_id=profile.id,
        category=data.category,
        terms=data.terms
    )
    db.add(term)
    db.commit()
    db.refresh(term)
    return {"status": "success", "data": term}
