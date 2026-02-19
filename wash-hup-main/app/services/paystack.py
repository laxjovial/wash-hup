from dotenv import load_dotenv
from fastapi import APIRouter, Request, BackgroundTasks, HTTPException
from app.api.dependencies import redis_dependency, db_dependency
from app.models.client.payment import Payment
from app.models.client.wash import Location, Wash
from app.models.washer.profile import Wallet
from app.models.washer.transaction import Transaction, Remittance
from app.websocket.router import manager
from app.core.logger import logger
from fastapi.responses import JSONResponse
from typing import Dict, Any
from uuid import uuid4
import hashlib
import hmac
import  json
import os
import httpx


load_dotenv()

BASE_URL = os.getenv("PAYSTACK_BASE_URL")
API_KEY = os.getenv("PAYSTACK_SECRET_KEY")


# Initialize client only if BASE_URL is provided, otherwise it will crash on startup
client = None
if BASE_URL:
    client = httpx.AsyncClient(
        base_url=BASE_URL,
        headers={"Authorization": f"Bearer {API_KEY}"},
        timeout=15
    )

async def get_paystack_client():
    if not client:
        raise HTTPException(status_code=503, detail="Paystack service not configured")
    return client

async def create_subaccount(fullname: str, bank_code: str, account_number: str, charge: float):
    pay_client = await get_paystack_client()
    url = "/subaccount"
    data = {
        "business_name": fullname, 
        "settlement_bank": bank_code, 
        "account_number": account_number, 
        "percentage_charge": charge
    }
    response = await pay_client.post(url, json=data)
    return response.json()

async def update_subaccount(subaccount_id: str, fullname: str, description: str, bank_code: str, account_number: str):
    pay_client = await get_paystack_client()
    url = f"/subaccount/{subaccount_id}"
    data = {
        "business_name": fullname, 
        "description": description, 
        "settlement_bank": bank_code, 
        "account_number": account_number
    }
    response = await pay_client.put(url, json=data)
    return response.json()

async def get_bank_list():
    pay_client = await get_paystack_client()
    url = "/bank"
    response = await pay_client.get(url)
    banks = [{"name": bank["name"], "code": bank["code"]} for bank in response.json()["data"]]
    return banks

async def initialize_payment(amount: int, email: str, subaccount: str):
    pay_client = await get_paystack_client()
    url = "/transaction/initialize"
    data = {
        "amount": str(amount*100),
        "email": email,
        "subaccount": subaccount
    }
    response = await pay_client.post(url, json=data)
    return response.json()



router = APIRouter(
    prefix="/paystack",
    tags=["Paystack"]
)

@router.post("/webhook")
async def paystack_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    redis: redis_dependency,
    db: db_dependency
):
    return await handle_paystack_webhook(request, background_tasks, redis, db)


async def handle_paystack_webhook(request: Request, background_tasks: BackgroundTasks, redis: redis_dependency, db: db_dependency):
    if not API_KEY:
         raise HTTPException(status_code=503, detail="Paystack API Key not configured")

    payload_bytes = await request.body()

    signature = request.headers.get("x-paystack-signature")
    if not signature:
        logger.warning("Webhook missing x-paystack-signature")
        raise HTTPException(status_code=400, detail="Missing signature")

    # Verify HMAC SHA512 signature
    expected = hmac.new(
        key=API_KEY.encode("utf-8"),
        msg=payload_bytes,
        digestmod=hashlib.sha512
    ).hexdigest()

    if not hmac.compare_digest(expected, signature):
        logger.warning("Invalid Paystack webhook signature")
        raise HTTPException(status_code=401, detail="Invalid signature")

    try:
        event = json.loads(payload_bytes)
        event_type = event.get("event")
        data = event.get("data", {})
    except json.JSONDecodeError:
        logger.error("Invalid JSON in webhook")
        raise HTTPException(status_code=400, detail="Invalid JSON")

    if event_type == "charge.success":
        background_tasks.add_task(process_charge_success, data, redis, db)
        logger.info(f"Queued charge.success processing for ref: {data.get('reference')}")

    return JSONResponse(status_code=200, content={"status": "success"})


async def process_charge_success(data: Dict[str, Any], redis: redis_dependency, db: db_dependency):
    reference = data.get("reference")

    if not reference:
        logger.error("charge.success webhook missing reference")
        return

    event_key = f"charge.success:{reference}"
    event = await redis.getex(event_key)

    if event:
        logger.info(f"Duplicate webhook ignored: {event_key}")
        return

    await redis.setex(event_key, 3600*24*30, json.dumps(data))

 
    amount = data.get("amount", 0) / 100
    logger.info(f"Processing successful payment Ref: {reference} | #{amount}")

    try:
        # Your real business logic here:
        split = data.get("fees_split")
        await create_settlement(db, reference, split)
        from pprint import pprint
        pprint(data.get("fees_split"))
        pass
    except Exception as exc:
        logger.exception(f"Failed to process charge.success for {reference}", exc_info=exc)
        # → In production: send to retry queue or alert system


async def create_settlement(db: db_dependency, reference: str, split):
    payment_model = db.query(Payment).filter(Payment.reference == reference).first()
    if not payment_model:
        logger.error(f"Payment not found for reference: {reference}")
        raise HTTPException(status_code=404, detail="Payment not found")

    wash_model = db.query(Wash).filter(Wash.id == payment_model.wash_id).first()
    if not wash_model:
        logger.error(f"Wash not found for wash_id: {payment_model.wash_id}")
        raise HTTPException(status_code=404, detail="Wash not found")
    
    location_model = db.query(Location).filter(Location.id == wash_model.location_id).first()
    if not location_model:
        logger.error(f"Location not found for wash_id: {payment_model.wash_id}")
        raise HTTPException(status_code=404, detail="Location not found")
    
    location = location_model.location

    payment_model.status = "completed"
    db.commit()

    transaction_model = Transaction(
        id=payment_model.id,
        wash_id=payment_model.wash_id,
        washer_id=payment_model.receiver_id,
        washer_name=payment_model.receiver_name,
        amount=split["subaccount"]/100,
        address=location
    )
    db.add(transaction_model)
    db.commit()
    db.refresh(transaction_model)

    wallet_model = db.query(Wallet).filter(Wallet.washer_id == payment_model.receiver_id).first()

    if not wallet_model:
        logger.error(f"Wallet not found for profile_id: {payment_model.receiver_id}")
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    wallet_model.balance += transaction_model.amount
    db.commit()

    amount = payment_model.amount-transaction_model.amount

    remittance_model = Remittance(
        id="re_"+str(uuid4()),
        washer_id=payment_model.receiver_id,
        Transaction_id=transaction_model.id,
        charge=split["params"]["percentage_charge"],
        amount=amount
    )
    db.add(remittance_model)
    db.commit()


    await manager.send_personal({
        "action": "transaction",
        "sender": payment_model.sender_id,
        "amount": payment_model.amount,
        "message": f"payment of {payment_model.amount} for wash {payment_model.wash_id} has been sent successfully"
    }, payment_model.receiver_id)

    await manager.send_personal({
        "action": "notification",
        "sender": "system",
        "message": f"payment of {payment_model.amount} for wash {payment_model.wash_id} has been sent successfully"
    }, payment_model.sender_id)
