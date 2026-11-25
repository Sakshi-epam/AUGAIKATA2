import csv
from decimal import Decimal

PORTFOLIOS = {
    "POR001": {"cash": 15000, "restricted": ["XYZCORP"], "max_pct": "0.10",
               "holdings": [("TCS", 50, 310), ("RELIANCE", 10, 2400)]},
    "POR002": {"cash": 10000, "restricted": [], "max_pct": "0.25",
               "holdings": [("INFY", 20, 1500)]},
    "POR003": {"cash": 100000, "restricted": ["BADCO"], "max_pct": "0.30",
               "holdings": [("RELIANCE", 30, 2400), ("TCS", 100, 310)]},
    "POR004": {"cash": 50000, "restricted": [], "max_pct": "0.50",
               "holdings": [("GOOGL", 5, 2100)]},
    "POR005": {"cash": 5000, "restricted": ["PENNY1"], "max_pct": "0.70",
               "holdings": [("INFY", 2, 1500)]},
}


def num(x):
    try:
        return Decimal(str(x).strip())
    except Exception:
        return None


def check_trade(t):
    action = t["action"].strip()
    qty, price = num(t["quantity"]), num(t["price"])
    sec = t["security_id"].strip()

    if qty is None or price is None or qty <= 0 or price <= 0 or action not in ("Buy", "Sell"):
        return "Rejected", "Invalid trade data."

    p = PORTFOLIOS.get(t["portfolio_id"].strip())
    if p is None:
        return "Rejected", "Unknown portfolio."

    if sec in p["restricted"]:
        return "Rejected", "Security is restricted for this portfolio."

    held = sum((Decimal(q) for s, q, _ in p["holdings"] if s == sec), Decimal(0))

    if action == "Sell":
        if held < qty:
            return "Rejected", "Insufficient holdings to sell."
        return "Approved", "All checks passed."

    
    cash = Decimal(p["cash"])
    if qty * price > cash:
        return "Rejected", "Insufficient cash for this buy order."

  
    post_cash = cash - qty * price
    post_value = (held + qty) * price
    others = sum((Decimal(q) * Decimal(m) for s, q, m in p["holdings"] if s != sec), Decimal(0))
    total = post_cash + post_value + others
    if post_value / total > Decimal(p["max_pct"]):
        return "Needs Manual Sign-off", "Exceeds maximum position concentration - requires approval."

   
    return "Approved", "All checks passed."


with open("trades_test.csv", newline="", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        decision, reason = check_trade(row)
        print(f"{row['portfolio_id']} {row['security_id']:9} {row['action']:4} "
              f"{row['quantity']:>4} @ {row['price']:>5} -> {decision}: {reason}")