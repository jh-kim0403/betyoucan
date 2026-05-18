from uuid import UUID
from sqlalchemy.orm import Session
from src.models import auth_schemas
from src.models.bounty_schemas import BountyLedger

def apply_bounty_ledger_entry(
    user_id: UUID,
    goal_id: UUID | None,
    ledger_type: str,
    bounty_amount: int,
    db: Session,
):
    user = db.query(auth_schemas.User).filter(auth_schemas.User.id == user_id).first()
    if not user:
        raise ValueError("User not found for bounty ledger entry")

    
    
    # Hold deducts at goal creation. Forfeit records terminal loss but does not
    # change available balance a second time.
    if ledger_type in ("fund", "release", "refund"):
        next_balance = user.bounty_balance + bounty_amount
    elif ledger_type == "forfeit":
        next_balance = user.bounty_balance
    else:
        next_balance = user.bounty_balance - bounty_amount

    if next_balance < 0:
        raise ValueError("Insufficient bounty balance for ledger entry")

    user.bounty_balance = next_balance
    bounty_ledger = BountyLedger(
        user_id=user_id,
        goal_id=goal_id,
        amount=bounty_amount,
        type=ledger_type,
    )
    db.add(bounty_ledger)
