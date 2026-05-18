import logging
import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from src.helpers.limiter import limiter
from src.helpers.bounty_ledger_utils import apply_bounty_ledger_entry
from src.helpers.stripe_utils import construct_webhook_event, StripeWebhookError
from src.helpers.auth_utils import validate_access_token
from src.helpers.db import get_db
from src.models.bounty_schemas import BountyTransaction
from uuid import UUID
from src.config import settings
from src.models.payment_models import CreatePaymentIntentRequest, CreatePaymentIntentResponse

router = APIRouter(prefix="/api/v1/payments", tags=["payments"])

STRIPE_SECRET_KEY = settings.stripe_secret_key
STRIPE_WEBHOOK_SECRET = settings.stripe_webhook_secret
if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY

MIN_BANK_CENTS = 500
MIN_CARD_CENTS = 1000



@router.post("/create-payment-intent", response_model=CreatePaymentIntentResponse)
@limiter.limit("10/minute")
def create_payment_intent(
    request: Request,
    payload: CreatePaymentIntentRequest,
    user_id: UUID = Depends(validate_access_token),
    db: Session = Depends(get_db),
):
    if not STRIPE_SECRET_KEY:
        raise HTTPException(status_code=500, detail="Stripe secret key not configured")

    method = payload.method.lower().strip()
    if method not in {"bank", "card"}:
        raise HTTPException(status_code=400, detail="Invalid payment method")

    amount_cents = int(payload.amount_cents)
    if method == "bank" and amount_cents < MIN_BANK_CENTS:
        raise HTTPException(status_code=400, detail="Minimum bank charge is $5")
    if method == "card" and amount_cents < MIN_CARD_CENTS:
        raise HTTPException(status_code=400, detail="Minimum card charge is $10")

    payment_method_types = ["us_bank_account"] if method == "bank" else ["card"]
    try:
        intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency="usd",
            payment_method_types=payment_method_types,
        )
    except stripe.error.StripeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    transaction = BountyTransaction(
        user_id=user_id,
        amount=amount_cents,
        direction="deposit",
        status="pending",
        payment_intent_id=intent.id,
    )
    db.add(transaction)
    db.commit()

    return CreatePaymentIntentResponse(
        client_secret=intent.client_secret,
        payment_intent_id=intent.id,
    )


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    logging.info("starting webhook api")
    if not STRIPE_WEBHOOK_SECRET:
        logging.info("Something")
        raise HTTPException(status_code=500, detail="Stripe webhook secret not configured")
        

    logging.info("awaiting body")
    payload = await request.body()
    logging.info("Received payload")
    sig_header = request.headers.get("stripe-signature")
    if not sig_header:
        raise HTTPException(status_code=400, detail="Missing Stripe signature")

    try:
        event = construct_webhook_event(
            payload=payload,
            sig_header=sig_header,
            webhook_secret=STRIPE_WEBHOOK_SECRET,
        )
    except StripeWebhookError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    logging.info("event received")
    event_type = event.get("type")
    data_object = event.get("data", {}).get("object", {})
    payment_intent_id = data_object.get("id")
    logging.info("payment_intent_id")
    if payment_intent_id:
        transaction = (
            db.query(BountyTransaction)
            .filter(BountyTransaction.payment_intent_id == payment_intent_id)
            .first()
        )
        if transaction:
            if event_type == "payment_intent.succeeded":
                if transaction.status != "succeeded":
                    transaction.status = "succeeded"
                    charge_id = data_object.get("latest_charge")
                    if charge_id:
                        transaction.charge_id = charge_id
                    apply_bounty_ledger_entry(
                        user_id=transaction.user_id,
                        goal_id=None,
                        ledger_type="fund",
                        bounty_amount=transaction.amount,
                        db=db,
                    )
            elif event_type == "payment_intent.payment_failed":
                transaction.status = "failed"
            elif event_type == "payment_intent.processing":
                transaction.status = "pending"
            db.commit()

    return {"ok": True}
