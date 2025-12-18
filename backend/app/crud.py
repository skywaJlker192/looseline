from decimal import Decimal
from typing import Iterable, List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models


def calculate_potential_win(amount: Decimal, coefficient: Decimal) -> dict:
  payout = round(amount * coefficient, 2)
  profit = round(payout - amount, 2)
  return {"payout": payout, "profit": profit}


def calculate_coupon_win(amount: Decimal, coefficients: Iterable[Decimal]) -> dict:
  coeffs = [Decimal(str(c)) for c in coefficients if Decimal(str(c)) >= Decimal("1.01")]
  if not coeffs or amount <= 0:
    return {
      "betAmount": Decimal("0"),
      "coefficients": [],
      "totalCoefficient": Decimal("0"),
      "potentialWin": Decimal("0"),
      "profit": Decimal("0"),
    }

  total_coeff = Decimal("1")
  for c in coeffs:
    total_coeff *= c

  potential = round(amount * total_coeff, 2)
  profit = round(potential - amount, 2)

  return {
    "betAmount": amount,
    "coefficients": coeffs,
    "totalCoefficient": round(total_coeff, 2),
    "potentialWin": potential,
    "profit": profit,
  }


def create_bet(db: Session, *, payload) -> models.Bet:
  data = payload.dict()
  if not data.get("potential_win"):
    calc = calculate_potential_win(payload.bet_amount, payload.coefficient)
    data["potential_win"] = calc["payout"]

  bet = models.Bet(**data)
  db.add(bet)
  db.commit()
  db.refresh(bet)
  return bet


def get_bet(db: Session, bet_id: int) -> Optional[models.Bet]:
  return db.get(models.Bet, bet_id)


def list_user_bets(db: Session, user_id: str) -> List[models.Bet]:
  stmt = select(models.Bet).where(models.Bet.user_id == user_id).order_by(
    models.Bet.placed_at.desc()
  )
  return list(db.scalars(stmt))


def create_coupon(db: Session, *, user_id: str, bet_ids: List[int], total_amount: Decimal) -> models.Coupon:
  # Получаем ставки и их коэффициенты
  stmt = select(models.Bet).where(models.Bet.bet_id.in_(bet_ids))
  bets = list(db.scalars(stmt))
  if len(bets) != len(bet_ids):
    raise ValueError("Some bet ids not found")

  coeffs = [Decimal(str(b.coefficient)) for b in bets]
  calc = calculate_coupon_win(total_amount, coeffs)

  from datetime import datetime

  date = datetime.utcnow().strftime("%Y%m%d")
  import random

  random_code = f"{random.randrange(10**6):06d}"
  coupon_code = f"CPN{date}_{random_code}"

  coupon = models.Coupon(
    user_id=user_id,
    coupon_code=coupon_code,
    total_bet_amount=total_amount,
    total_potential_win=calc["potentialWin"],
    status="open",
    number_of_bets=len(bet_ids),
  )
  db.add(coupon)
  db.flush()  # чтобы появился coupon_id

  for b in bets:
    link = models.CouponBet(coupon_id=coupon.coupon_id, bet_id=b.bet_id)
    db.add(link)

  db.commit()
  db.refresh(coupon)
  return coupon


def update_bet_status(db: Session, bet_id: int, new_status: str) -> Optional[models.Bet]:
  bet = get_bet(db, bet_id)
  if not bet:
    return None
  bet.status = new_status
  db.commit()
  db.refresh(bet)
  return bet


