"""
Metrics API Endpoints — includes FY multi-year data and comparison
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime
import math

router = APIRouter()

# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────

def _current_fy() -> int:
    """Return current fiscal year (calendar year, Jan-Dec)."""
    return datetime.now().year


def _fy_sales(fy: int) -> Dict[str, Any]:
    """Generate deterministic mock sales data for a given fiscal year."""
    base = 1_000_000 * (1 + (fy - 2022) * 0.12)   # 12 % CAGR baseline
    factor = 1 + math.sin(fy) * 0.05               # slight year-over-year variation
    rev = round(base * factor)
    expected = round(rev / 0.85)
    return {
        "fiscal_year": fy,
        "period": f"FY {fy}",
        "metrics": {
            "total_revenue": rev,
            "expected_revenue": expected,
            "revenue_drop_percentage": round((expected - rev) / expected * 100, 1),
            "conversion_rate": round(0.22 + (fy - 2022) * 0.005, 3),
            "average_deal_size": round(42_000 + (fy - 2022) * 1_500),
            "pipeline_value": round(rev * 2.9),
            "active_deals": 140 + (fy - 2022) * 8,
            "closed_deals": 80 + (fy - 2022) * 5,
            "win_rate": round(0.54 + (fy - 2022) * 0.01, 2),
        },
        "regional_performance": {
            "North America": {
                "revenue": round(rev * 0.53),
                "growth": round(-14 + (fy - 2022) * 1.5, 1),
                "deals": 42 + (fy - 2022) * 2,
            },
            "Europe": {
                "revenue": round(rev * 0.33),
                "growth": round(-20 + (fy - 2022) * 2.0, 1),
                "deals": 26 + (fy - 2022) * 1,
            },
            "Asia Pacific": {
                "revenue": round(rev * 0.14),
                "growth": round(-12 + (fy - 2022) * 2.5, 1),
                "deals": 14 + (fy - 2022) * 1,
            },
        },
        "top_products": [
            {"name": "Enterprise Suite",   "revenue": round(rev * 0.40), "units": 60 + (fy - 2022) * 4},
            {"name": "Professional Plan",  "revenue": round(rev * 0.34), "units": 130 + (fy - 2022) * 8},
            {"name": "Starter Package",    "revenue": round(rev * 0.26), "units": 340 + (fy - 2022) * 20},
        ],
        "trends": [
            "Revenue declining for 3 consecutive months" if fy == _current_fy() else "Revenue recovering steadily",
            "Conversion rate below industry average" if rev < 9_000_000 else "Conversion rate on target",
            "Pipeline value stable but deal velocity decreasing",
        ],
        "status": "warning" if rev < 9_000_000 else "healthy",
        "alert_level": "high" if rev < 9_000_000 else "low",
        "timestamp": datetime.now().isoformat(),
    }


def _fy_finance(fy: int) -> Dict[str, Any]:
    cash     = round(12_000_000 + (fy - 2022) * 1_200_000)
    burn     = round(1_100_000  + (fy - 2022) * 50_000)
    revenue  = round(9_000_000  + (fy - 2022) * 800_000)
    expenses = round(7_500_000  + (fy - 2022) * 600_000)
    ebitda   = round(1_600_000  + (fy - 2022) * 200_000)

    # Derived P&L metrics
    # EBIT = EBITDA minus D&A (assumed ~8% of revenue)
    da            = round(revenue * 0.08)
    ebit          = ebitda - da
    # Interest expense (modest debt servicing)
    interest      = round(revenue * 0.015)
    # Earnings before tax
    ebt           = ebit - interest
    # Tax at 21% effective rate
    tax_rate      = 0.21
    tax           = round(ebt * tax_rate)
    # Net Income = EBT − Tax  (also called Profit After Tax / Earnings After Tax)
    net_income    = ebt - tax
    # PAT and EAT are the same figure as net income in this P&L structure
    profit_after_tax    = net_income
    earnings_after_tax  = net_income

    return {
        "fiscal_year": fy,
        "period": f"FY {fy}",
        "metrics": {
            "cash_balance":         cash,
            "burn_rate":            burn,
            "runway_months":        round(cash / burn, 1),
            "gross_margin":         round(0.68 + (fy - 2022) * 0.015, 3),
            "operating_margin":     round(0.15 + (fy - 2022) * 0.01, 3),
            "ebitda":               ebitda,
            "revenue":              revenue,
            "expenses":             expenses,
            # P&L waterfall
            "depreciation_amortization": da,
            "ebit":                 ebit,
            "interest_expense":     interest,
            "earnings_before_tax":  ebt,
            "tax_expense":          tax,
            "net_income":           net_income,
            "profit_after_tax":     profit_after_tax,
            "earnings_after_tax":   earnings_after_tax,
        },
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
    }


def _fy_operations(fy: int) -> Dict[str, Any]:
    return {
        "fiscal_year": fy,
        "period": f"FY {fy}",
        "metrics": {
            "customer_satisfaction": round(4.0 + (fy - 2022) * 0.08, 1),
            "nps_score":             42 + (fy - 2022) * 3,
            "support_tickets":       240 - (fy - 2022) * 5,
            "avg_resolution_time":   round(4.8 - (fy - 2022) * 0.2, 1),
            "system_uptime":         round(99.5 + (fy - 2022) * 0.1, 1),
            "active_users":          10_000 + (fy - 2022) * 1_500,
        },
        "status": "good",
        "timestamp": datetime.now().isoformat(),
    }


# ─────────────────────────────────────────────
#  Sales endpoints
# ─────────────────────────────────────────────

@router.get("/sales")
async def get_sales_metrics(fy: Optional[int] = Query(None, description="Fiscal year (e.g. 2025)")) -> Dict[str, Any]:
    """Get sales metrics for a given FY (defaults to current year)."""
    try:
        return _fy_sales(fy or _current_fy())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sales/fy")
async def get_sales_fy_range() -> Dict[str, Any]:
    """Return sales metrics for the current FY and previous two FYs."""
    cy = _current_fy()
    years = [cy, cy - 1, cy - 2]
    data = {str(y): _fy_sales(y) for y in years}
    return {"fiscal_years": years, "data": data, "timestamp": datetime.now().isoformat()}


@router.get("/sales/compare")
async def compare_sales(
    fy1: int = Query(..., description="First fiscal year"),
    fy2: int = Query(..., description="Second fiscal year"),
) -> Dict[str, Any]:
    """Compare sales metrics between two fiscal years."""
    d1, d2 = _fy_sales(fy1), _fy_sales(fy2)
    m1, m2 = d1["metrics"], d2["metrics"]

    def pct_change(a, b):
        return round((b - a) / a * 100, 1) if a else None

    comparison = {k: {"fy1": m1[k], "fy2": m2[k], "change_pct": pct_change(m1[k], m2[k])}
                  for k in m1 if isinstance(m1[k], (int, float))}
    return {
        "fy1": fy1, "fy2": fy2,
        "comparison": comparison,
        "regional_comparison": {
            region: {
                "fy1_revenue": d1["regional_performance"][region]["revenue"],
                "fy2_revenue": d2["regional_performance"][region]["revenue"],
                "change_pct":  pct_change(d1["regional_performance"][region]["revenue"],
                                           d2["regional_performance"][region]["revenue"]),
            }
            for region in d1["regional_performance"]
        },
        "timestamp": datetime.now().isoformat(),
    }


# ─────────────────────────────────────────────
#  Finance endpoints
# ─────────────────────────────────────────────

@router.get("/finance")
async def get_finance_metrics(fy: Optional[int] = Query(None)) -> Dict[str, Any]:
    try:
        return _fy_finance(fy or _current_fy())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/finance/fy")
async def get_finance_fy_range() -> Dict[str, Any]:
    cy = _current_fy()
    years = [cy, cy - 1, cy - 2]
    data = {str(y): _fy_finance(y) for y in years}
    return {"fiscal_years": years, "data": data, "timestamp": datetime.now().isoformat()}


@router.get("/finance/compare")
async def compare_finance(
    fy1: int = Query(...),
    fy2: int = Query(...),
) -> Dict[str, Any]:
    d1, d2 = _fy_finance(fy1), _fy_finance(fy2)
    m1, m2 = d1["metrics"], d2["metrics"]

    def pct_change(a, b):
        return round((b - a) / a * 100, 1) if a else None

    comparison = {k: {"fy1": m1[k], "fy2": m2[k], "change_pct": pct_change(m1[k], m2[k])}
                  for k in m1 if isinstance(m1[k], (int, float))}
    return {"fy1": fy1, "fy2": fy2, "comparison": comparison, "timestamp": datetime.now().isoformat()}


# ─────────────────────────────────────────────
#  Operations endpoints
# ─────────────────────────────────────────────

@router.get("/operations")
async def get_operations_metrics(fy: Optional[int] = Query(None)) -> Dict[str, Any]:
    try:
        return _fy_operations(fy or _current_fy())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/operations/fy")
async def get_operations_fy_range() -> Dict[str, Any]:
    cy = _current_fy()
    years = [cy, cy - 1, cy - 2]
    data = {str(y): _fy_operations(y) for y in years}
    return {"fiscal_years": years, "data": data, "timestamp": datetime.now().isoformat()}


@router.get("/operations/compare")
async def compare_operations(
    fy1: int = Query(...),
    fy2: int = Query(...),
) -> Dict[str, Any]:
    d1, d2 = _fy_operations(fy1), _fy_operations(fy2)
    m1, m2 = d1["metrics"], d2["metrics"]

    def pct_change(a, b):
        return round((b - a) / a * 100, 1) if a else None

    comparison = {k: {"fy1": m1[k], "fy2": m2[k], "change_pct": pct_change(m1[k], m2[k])}
                  for k in m1 if isinstance(m1[k], (int, float))}
    return {"fy1": fy1, "fy2": fy2, "comparison": comparison, "timestamp": datetime.now().isoformat()}


# ─────────────────────────────────────────────
#  Summary
# ─────────────────────────────────────────────

@router.get("/summary")
async def get_metrics_summary() -> Dict[str, Any]:
    cy = _current_fy()
    s = _fy_sales(cy)
    f = _fy_finance(cy)
    o = _fy_operations(cy)
    try:
        summary = {
            "timestamp": datetime.now().isoformat(),
            "fiscal_year": cy,
            "overall_health": "warning",
            "key_metrics": {
                "revenue":      {"value": s["metrics"]["total_revenue"],       "change": -s["metrics"]["revenue_drop_percentage"], "status": "declining"},
                "customers":    {"value": 1_245 + (cy - 2024) * 50,           "change": -5.2,  "status": "declining"},
                "cash":         {"value": f["metrics"]["cash_balance"],        "change": 2.3,   "status": "stable"},
                "satisfaction": {"value": o["metrics"]["customer_satisfaction"],"change": -0.3, "status": "declining"},
            },
            "alerts": [
                {"severity": "high",   "category": "revenue",   "message": "Revenue dropped vs target", "timestamp": datetime.now().isoformat()},
                {"severity": "medium", "category": "customers", "message": "Customer churn rate increasing", "timestamp": datetime.now().isoformat()},
            ],
            "recommendations_count": 8,
            "active_simulations": 2,
        }
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────
#  Chat / AI Summarisation endpoint
# ─────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = None      # e.g. "sales", "finance", "operations"
    data_snapshot: Optional[Dict[str, Any]] = None

CANNED_INSIGHTS = {
    "sales": [
        "Revenue has grown by ~12% CAGR but remains below quarterly targets. North America leads at 53% share.",
        "Win rate is improving year-over-year. Consider focusing on the Enterprise Suite — it generates 40% of revenue.",
        "Deal velocity is the primary concern. Conversion rate is trending upward but still below industry average.",
        "Asia Pacific shows the strongest relative growth trajectory. Investing here could yield outsized returns.",
    ],
    "finance": [
        "Cash runway remains healthy (>12 months). Burn rate is within acceptable thresholds.",
        "Gross margin is improving quarter-over-quarter — a positive sign of operational efficiency.",
        "EBITDA growth is steady, but operating margin improvements are slowing. Review cost structure.",
        "Revenue and expenses are growing proportionally — maintain discipline to protect margins.",
    ],
    "operations": [
        "System uptime exceeds 99.5% — infrastructure is reliable. Focus energy on reducing ticket backlog.",
        "Customer satisfaction is trending positively. NPS improvement of 3 points year-over-year is notable.",
        "Average resolution time is decreasing — support team efficiency is improving.",
        "Active user growth of ~1,500 per year suggests healthy product adoption.",
    ],
    "general": [
        "Overall business health is cautiously positive. Revenue and operational metrics are improving year-over-year.",
        "Key risk areas: revenue vs target gap, customer churn rate. Monitor these closely.",
        "Strengths: strong cash position, improving margins, growing user base, high system reliability.",
        "Recommendation: prioritise sales pipeline acceleration and customer retention programmes.",
    ],
}

# ── Greeting / small-talk patterns ──────────────────────────────────────────
_GREETINGS = {
    # hello-type
    frozenset(["hi","hello","hey","hiya","howdy","sup","yo","greetings","salut","bonjour","hola","namaste","ciao","ahoy"]): None,
    # how-are-you type
    frozenset(["how are you","how r u","how are u","how do you do","how's it going","how you doing",
               "what's up","whats up","wazzup","you ok","are you ok","you good","you alright"]): None,
    # thanks
    frozenset(["thank","thanks","thx","ty","cheers","appreciate","grateful","gracias","merci","danke"]): None,
    # bye
    frozenset(["bye","goodbye","see you","cya","later","take care","farewell","night","good night","good bye"]): None,
    # who-are-you
    frozenset(["who are you","what are you","tell me about yourself","introduce yourself",
               "what can you do","what do you do","your name","who made you","are you ai",
               "are you a bot","are you human","are you real"]): None,
}

_GREETING_REPLIES: Dict[str, List[str]] = {
    "hello": [
        "Hello! 👋 I'm your Enterprise COO AI Assistant. Ask me about Sales, Finance, Operations, trends, risks, or recommendations.",
        "Hi there! Great to see you. I can help with business insights — revenue, cash flow, uptime, KPIs and more. What would you like to know?",
        "Hey! I'm here to help with your business data. Try asking: 'Show me a summary', 'What are the key risks?', or 'What do you recommend?'",
    ],
    "how_are_you": [
        "I'm doing great, thank you for asking! 😊 Ready to help you with business insights. What would you like to know?",
        "All systems operational! 🚀 I'm here and ready to assist. Ask me anything about Sales, Finance, or Operations.",
        "Feeling sharp and data-ready! What business question can I help you with today?",
    ],
    "thanks": [
        "You're welcome! 😊 Let me know if you have any other questions.",
        "Happy to help! Feel free to ask anything else about your business data.",
        "Anytime! I'm always here if you need more insights.",
    ],
    "bye": [
        "Goodbye! 👋 Come back anytime — your data is always here.",
        "See you later! Don't hesitate to return for more business insights.",
        "Take care! 🚀 Your dashboards will keep running smoothly.",
    ],
    "who": [
        "I'm the Enterprise Digital COO AI Assistant — built to help you understand your business data across Sales, Finance, and Operations. Ask me about KPIs, trends, risks, or recommendations.",
        "I'm an AI assistant specialised in enterprise business intelligence. I can analyse Sales performance, Financial health, and Operational metrics. How can I help?",
    ],
}

def _detect_greeting(msg: str) -> Optional[str]:
    """Return greeting category if the message is a greeting/small-talk, else None."""
    m = msg.lower().strip().rstrip("!?.,'\"")
    # Check multi-word phrases first
    for category, replies in [
        ("how_are_you", _GREETING_REPLIES["how_are_you"]),
        ("who",         _GREETING_REPLIES["who"]),
    ]:
        patterns = {
            "how_are_you": ["how are you","how r u","how are u","how do you do","how's it going",
                            "how you doing","what's up","whats up","wazzup","you ok","you good"],
            "who":         ["who are you","what are you","tell me about yourself","introduce yourself",
                            "what can you do","your name","who made you","are you ai","are you a bot"],
        }
        if any(p in m for p in patterns[category]):
            return category
    # Single-word / short checks
    tokens = set(m.split())
    if tokens & {"hi","hello","hey","hiya","howdy","sup","yo","greetings","hola","namaste","ciao","ahoy","bonjour"}:
        return "hello"
    if tokens & {"thank","thanks","thx","ty","cheers","appreciate","grateful","gracias","merci","danke"}:
        return "thanks"
    if tokens & {"bye","goodbye","cya","later","farewell","night"} or "see you" in m or "good bye" in m or "good night" in m:
        return "bye"
    return None


@router.post("/chat")
async def chat_summarise(req: ChatRequest) -> Dict[str, Any]:
    """
    Chat endpoint: handles greetings/small-talk first, then routes to
    contextual business insights based on the current page context.
    """
    ctx = (req.context or "general").lower()
    if ctx not in CANNED_INSIGHTS:
        ctx = "general"

    msg_lower = req.message.lower()

    # ── 1. Greeting / small-talk detection (highest priority) ──────────────
    greeting_cat = _detect_greeting(req.message)
    if greeting_cat:
        replies = _GREETING_REPLIES[greeting_cat]
        # Rotate through replies deterministically based on message length
        answer = replies[len(req.message) % len(replies)]
        return {
            "answer": answer,
            "context": "greeting",
            "timestamp": datetime.now().isoformat(),
            "suggestions": [
                "Show me a summary",
                "What are the key risks?",
                "What do you recommend?",
                "How are trends looking?",
            ],
        }

    # ── 2. Business insight matching ───────────────────────────────────────
    if any(w in msg_lower for w in ["summar", "overview", "tldr", "brief"]):
        answer = CANNED_INSIGHTS[ctx][0]
    elif any(w in msg_lower for w in ["risk", "concern", "problem", "issue", "warn", "alert"]):
        answer = CANNED_INSIGHTS[ctx][1] if len(CANNED_INSIGHTS[ctx]) > 1 else CANNED_INSIGHTS[ctx][0]
    elif any(w in msg_lower for w in ["recommend", "suggest", "action", "improve", "next"]):
        answer = CANNED_INSIGHTS[ctx][-1]
    elif any(w in msg_lower for w in ["trend", "trajectory", "growth", "decline"]):
        answer = CANNED_INSIGHTS[ctx][2] if len(CANNED_INSIGHTS[ctx]) > 2 else CANNED_INSIGHTS[ctx][0]
    else:
        idx = len(req.message) % len(CANNED_INSIGHTS[ctx])
        answer = CANNED_INSIGHTS[ctx][idx]

    # ── 3. Weave in live snapshot numbers if available ─────────────────────
    snapshot_note = ""
    if req.data_snapshot:
        m = req.data_snapshot.get("metrics", {})
        if ctx == "sales" and "total_revenue" in m:
            snapshot_note = f" (Current FY revenue: ${m['total_revenue']:,})"
        elif ctx == "finance" and "cash_balance" in m:
            snapshot_note = f" (Current cash balance: ${m['cash_balance']:,})"
        elif ctx == "operations" and "customer_satisfaction" in m:
            snapshot_note = f" (CSAT: {m['customer_satisfaction']}/5.0)"

    return {
        "answer": answer + snapshot_note,
        "context": ctx,
        "timestamp": datetime.now().isoformat(),
        "suggestions": [
            "What are the key risks?",
            "Show me a summary",
            "What do you recommend?",
            "How are trends looking?",
        ],
    }

# Made with Bob
