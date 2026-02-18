from fastapi import APIRouter, status, HTTPException, Body
from ...dependencies import admin_dependency, db_dependency, get_profile_model
from app.models.admin.profile import Faqs, TermsAndConditions, Category
from uuid import uuid4
from datetime import datetime
from typing import Optional


router = APIRouter(
    prefix="/site",
    tags=["Admin: Site Content"]
)

@router.get("/faqs", status_code=status.HTTP_200_OK)
async def get_faqs(db: db_dependency, admin: admin_dependency, category: Optional[Category] = None):
    query = db.query(Faqs)
    if category:
        query = query.filter(Faqs.category == category)
    faqs = query.all()
    return {"status": "success", "data": faqs}

@router.post("/faqs", status_code=status.HTTP_201_CREATED)
async def create_faq(
    db: db_dependency,
    admin: admin_dependency,
    category: Category = Body(...),
    question: str = Body(...),
    answer: str = Body(...)
):
    profile = get_profile_model(db, admin.get("id"))
    faq = Faqs(
        id="faq_"+str(uuid4()),
        admin_id=profile.id,
        category=category,
        question=question,
        answer=answer
    )
    db.add(faq)
    db.commit()
    db.refresh(faq)
    return {"status": "success", "data": faq}

@router.put("/faqs/{faq_id}", status_code=status.HTTP_200_OK)
async def update_faq(
    faq_id: str,
    db: db_dependency,
    admin: admin_dependency,
    question: Optional[str] = Body(None),
    answer: Optional[str] = Body(None)
):
    faq = db.query(Faqs).filter(Faqs.id == faq_id).first()
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")

    if question: faq.question = question
    if answer: faq.answer = answer

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

@router.post("/terms", status_code=status.HTTP_201_CREATED)
async def create_terms(
    db: db_dependency,
    admin: admin_dependency,
    category: Category = Body(...),
    terms_text: str = Body(...)
):
    profile = get_profile_model(db, admin.get("id"))
    term = TermsAndConditions(
        id="term_"+str(uuid4()),
        admin_id=profile.id,
        category=category,
        terms=terms_text
    )
    db.add(term)
    db.commit()
    db.refresh(term)
    return {"status": "success", "data": term}
