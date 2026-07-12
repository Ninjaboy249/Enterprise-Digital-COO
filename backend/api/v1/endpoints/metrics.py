"""
Metrics API Endpoints — includes FY multi-year data and comparison
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime
import math
import re
import os
import logging

logger = logging.getLogger(__name__)

# ── OpenAI client (optional — graceful fallback to canned responses) ──────────
try:
    from openai import AsyncOpenAI
    _openai_key = os.getenv("OPENAI_API_KEY", "")
    _openai_client: Optional[AsyncOpenAI] = AsyncOpenAI(api_key=_openai_key) if _openai_key and _openai_key != "your-openai-api-key" else None
    _openai_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
except ImportError:
    _openai_client = None
    _openai_model = "gpt-3.5-turbo"

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

# ── Input validation helpers ───────────────────────────────────────────────────

# Minimum meaningful word count for a business query
_MIN_WORDS = 1
# Ratio of printable ASCII to total chars; below this = gibberish
_MIN_PRINTABLE_RATIO = 0.70
# Max repeated-char run (e.g. "aaaaaaa" or "@@@@@")
_MAX_CHAR_RUN = 4
# Regex: message must contain at least one letter
_HAS_LETTER = re.compile(r"[a-zA-Z]")

def _is_valid_query(msg: str) -> bool:
    """Return False for gibberish, symbol-spam, or non-text inputs."""
    stripped = msg.strip()
    if not stripped:
        return False
    # Must contain at least one letter
    if not _HAS_LETTER.search(stripped):
        return False
    # Reject if more than 60% non-printable / non-ASCII
    printable = sum(1 for c in stripped if c.isprintable() and ord(c) < 128)
    if len(stripped) > 0 and (printable / len(stripped)) < _MIN_PRINTABLE_RATIO:
        return False
    # Reject long runs of the same character (e.g. "@@@@@@@@" or "aaaaaaaa")
    if re.search(r"(.)\1{" + str(_MAX_CHAR_RUN) + r",}", stripped):
        return False
    # Reject if almost all chars are special symbols (no semantic value)
    letter_count = sum(1 for c in stripped if c.isalpha())
    if len(stripped) > 3 and letter_count / len(stripped) < 0.25:
        return False
    return True

_INVALID_QUERY_RESPONSE = {
    "answer": (
        "I couldn't understand that query. Please ask a business question — for example: "
        "\"What happened to revenue this quarter?\", \"Show me a cash flow summary\", "
        "or \"What are the top risks?\""
    ),
    "context": "error",
    "suggestions": [
        "What happened to revenue?",
        "Show me a summary",
        "What are the key risks?",
        "What do you recommend?",
    ],
}

_DEFAULT_HELP_LINE = (
    "You can also ask me about Sales, Finance, Operations, trends, risks, or recommendations."
)
_CREATOR_RESPONSE = (
    "I was created by Shivam Roy (Regression Team). "
    "I'm your Enterprise Digital COO AI Assistant, built to help with business insight and quick questions. "
    f"{_DEFAULT_HELP_LINE}"
)


class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = None          # e.g. "sales", "finance", "operations"
    data_snapshot: Optional[Dict[str, Any]] = None   # single-domain snapshot (sub-pages)
    live_data: Optional[Dict[str, Any]] = None       # full allFYData from index (all domains)

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
        "I'm the Enterprise Digital COO AI Assistant, created by Shivam Roy (Regression Team). I help you understand business data across Sales, Finance, and Operations. Ask me about KPIs, trends, risks, or recommendations.",
        "I'm an AI assistant created by Shivam Roy (Regression Team), specialised in enterprise business intelligence. I can analyse Sales performance, Financial health, and Operational metrics. How can I help?",
    ],
}

def _is_creator_query(msg: str) -> bool:
    """Detect creator/owner/build-origin questions before model routing."""
    m = msg.lower().strip()
    subject_hit = any(term in m for term in ["you", "this", "assistant", "coo", "dashboard", "app", "project", "system"])
    creator_hit = any(term in m for term in ["created", "creator", "made", "built", "developed", "author", "owner", "invented"])
    if subject_hit and creator_hit:
        return True
    return any(
        phrase in m
        for phrase in [
            "who made you",
            "who built you",
            "who created you",
            "who developed you",
            "who is your creator",
            "who owns you",
        ]
    )

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


def _build_data_brief(req: "ChatRequest") -> str:
    """
    Assemble a concise, plain-English data brief from whatever live data
    is available in the request.  Returns an empty string if no data.
    """
    lines: list[str] = []
    fy_label = ""

    # ── Full allFYData bundle (sent from index.html) ───────────────────────
    if req.live_data:
        ld = req.live_data
        # Sales
        s_data = ld.get("sales", {}).get("data", {})
        if s_data:
            for fy, fy_obj in sorted(s_data.items(), reverse=True)[:1]:   # current FY only
                fy_label = f"FY {fy}"
                m = fy_obj.get("metrics", {})
                lines.append(f"[Sales — {fy_label}]")
                if "total_revenue" in m:
                    lines.append(f"  Revenue: ${m['total_revenue']:,.0f}  (expected: ${m.get('expected_revenue', 0):,.0f})")
                    drop = m.get("revenue_drop_percentage")
                    if drop:
                        lines.append(f"  Revenue vs target: -{drop}%")
                if "conversion_rate" in m:
                    lines.append(f"  Conversion rate: {m['conversion_rate']*100:.1f}%  |  Win rate: {m.get('win_rate',0)*100:.0f}%")
                if "pipeline_value" in m:
                    lines.append(f"  Pipeline: ${m['pipeline_value']:,.0f}  |  Active deals: {m.get('active_deals',0)}")
                reg = fy_obj.get("regional_performance", {})
                if reg:
                    lines.append("  Regional: " + "  ".join(
                        f"{r}: ${v['revenue']:,.0f} ({v['growth']:+.1f}%)" for r, v in reg.items()
                    ))
        # Finance
        f_data = ld.get("finance", {}).get("data", {})
        if f_data:
            for fy, fy_obj in sorted(f_data.items(), reverse=True)[:1]:
                m = fy_obj.get("metrics", {})
                lines.append(f"[Finance — FY {fy}]")
                if "cash_balance" in m:
                    lines.append(f"  Cash: ${m['cash_balance']:,.0f}  |  Burn rate: ${m.get('burn_rate',0):,.0f}/mo")
                    lines.append(f"  Runway: {m.get('runway_months',0):.1f} months")
                if "gross_margin" in m:
                    lines.append(f"  Gross margin: {m['gross_margin']*100:.1f}%  |  EBITDA: ${m.get('ebitda',0):,.0f}")
                if "net_income" in m:
                    lines.append(f"  Net income: ${m['net_income']:,.0f}  |  Operating margin: {m.get('operating_margin',0)*100:.1f}%")
        # Operations
        o_data = ld.get("operations", {}).get("data", {})
        if o_data:
            for fy, fy_obj in sorted(o_data.items(), reverse=True)[:1]:
                m = fy_obj.get("metrics", {})
                lines.append(f"[Operations — FY {fy}]")
                if "customer_satisfaction" in m:
                    lines.append(f"  CSAT: {m['customer_satisfaction']}/5.0  |  NPS: {m.get('nps_score','–')}")
                if "active_users" in m:
                    lines.append(f"  Active users: {m['active_users']:,}  |  Uptime: {m.get('system_uptime','–')}%")
                if "support_tickets" in m:
                    lines.append(f"  Support tickets: {m['support_tickets']}  |  Avg resolution: {m.get('avg_resolution_time','–')}h")

    # ── Single-domain snapshot (sent from sub-pages) ───────────────────────
    elif req.data_snapshot:
        m = req.data_snapshot.get("metrics", {})
        fy = req.data_snapshot.get("fiscal_year", "")
        period = req.data_snapshot.get("period", f"FY {fy}" if fy else "")
        ctx = (req.context or "general").lower()
        if ctx == "sales":
            lines.append(f"[Sales — {period}]")
            for key in ["total_revenue", "expected_revenue", "revenue_drop_percentage",
                        "conversion_rate", "win_rate", "pipeline_value", "active_deals"]:
                if key in m:
                    val = m[key]
                    if isinstance(val, float) and val < 2:
                        lines.append(f"  {key}: {val*100:.1f}%")
                    elif isinstance(val, (int, float)) and val > 1000:
                        lines.append(f"  {key}: ${val:,.0f}")
                    else:
                        lines.append(f"  {key}: {val}")
        elif ctx == "finance":
            lines.append(f"[Finance — {period}]")
            for key in ["cash_balance", "burn_rate", "runway_months", "gross_margin",
                        "operating_margin", "ebitda", "net_income", "revenue", "expenses"]:
                if key in m:
                    val = m[key]
                    if key in ("gross_margin", "operating_margin"):
                        lines.append(f"  {key}: {val*100:.1f}%")
                    elif isinstance(val, (int, float)) and val > 100:
                        lines.append(f"  {key}: ${val:,.0f}")
                    else:
                        lines.append(f"  {key}: {val}")
        elif ctx == "operations":
            lines.append(f"[Operations — {period}]")
            for key in ["customer_satisfaction", "nps_score", "support_tickets",
                        "avg_resolution_time", "system_uptime", "active_users"]:
                if key in m:
                    lines.append(f"  {key}: {m[key]}")

    return "\n".join(lines)


def _money(value: Any) -> str:
    if isinstance(value, (int, float)):
        return f"${value:,.0f}"
    return str(value)


def _percent(value: Any) -> str:
    if isinstance(value, (int, float)):
        return f"{value * 100:.1f}%" if abs(value) <= 1 else f"{value:.1f}%"
    return str(value)


def _latest_domain_snapshot(req: "ChatRequest", ctx: str) -> Dict[str, Any]:
    if req.data_snapshot:
        return req.data_snapshot

    if req.live_data:
        domain_data = req.live_data.get(ctx, {}).get("data", {})
        if domain_data:
            return sorted(
                domain_data.values(),
                key=lambda item: item.get("fiscal_year", 0),
                reverse=True,
            )[0]

    fy = _current_fy()
    if ctx == "sales":
        return _fy_sales(fy)
    if ctx == "finance":
        return _fy_finance(fy)
    if ctx == "operations":
        return _fy_operations(fy)
    return {}


def _metric_fallback_answer(req: "ChatRequest", ctx: str, msg_lower: str) -> str:
    """
    Deterministic COO-style answer used when OpenAI is not configured or fails.
    It stays grounded in current dashboard numbers instead of rotating canned text.
    """
    if ctx == "general":
        fy = _current_fy()
        sales = _latest_domain_snapshot(req, "sales") or _fy_sales(fy)
        finance = _latest_domain_snapshot(req, "finance") or _fy_finance(fy)
        ops = _latest_domain_snapshot(req, "operations") or _fy_operations(fy)
        sm, fm, om = sales.get("metrics", {}), finance.get("metrics", {}), ops.get("metrics", {})
        return (
            f"Here is the current COO story: sales revenue is {_money(sm.get('total_revenue', 0))} "
            f"against an expected {_money(sm.get('expected_revenue', 0))}, so the revenue gap is "
            f"{sm.get('revenue_drop_percentage', 0)}%. Finance is stable with {_money(fm.get('cash_balance', 0))} "
            f"cash and {fm.get('runway_months', 0)} months of runway. Operations are healthy at "
            f"{om.get('system_uptime', 0)}% uptime and {om.get('customer_satisfaction', 0)}/5 CSAT. "
            "Next move: protect cash, accelerate high-probability pipeline, and keep support response time low."
        )

    snap = _latest_domain_snapshot(req, ctx)
    metrics = snap.get("metrics", {})
    period = snap.get("period") or f"FY {snap.get('fiscal_year', _current_fy())}"
    wants_risk = any(w in msg_lower for w in ["risk", "concern", "problem", "issue", "warn", "alert", "why", "happened"])
    wants_action = any(w in msg_lower for w in ["recommend", "suggest", "action", "improve", "next", "do"])
    wants_summary = any(w in msg_lower for w in ["summar", "overview", "brief", "status", "how"])

    if ctx == "sales":
        revenue = metrics.get("total_revenue", 0)
        expected = metrics.get("expected_revenue", 0)
        gap = metrics.get("revenue_drop_percentage", 0)
        pipeline = metrics.get("pipeline_value", 0)
        win_rate = metrics.get("win_rate", 0)
        deals = metrics.get("active_deals", 0)
        base = (
            f"For {period}, sales revenue is {_money(revenue)} versus an expected {_money(expected)}, "
            f"leaving a {gap}% revenue gap. Pipeline is {_money(pipeline)} across {deals} active deals, "
            f"with win rate at {_percent(win_rate)}."
        )
        if wants_risk:
            return f"{base} The main risk is not demand volume; it is conversion and deal velocity. Focus weekly inspection on late-stage deals, blocked enterprise opportunities, and regions under target."
        if wants_action:
            return f"{base} Next move: pull forward high-probability enterprise deals, assign owners to stalled opportunities, and protect pricing on the largest pipeline accounts."
        if wants_summary:
            return f"{base} The business story is a strong pipeline with a target gap that needs sharper execution."
        return f"{base} I would treat this as a pipeline execution issue and prioritize conversion, deal velocity, and enterprise close plans."

    if ctx == "finance":
        cash = metrics.get("cash_balance", 0)
        burn = metrics.get("burn_rate", 0)
        runway = metrics.get("runway_months", 0)
        gross_margin = metrics.get("gross_margin", 0)
        ebitda = metrics.get("ebitda", 0)
        net_income = metrics.get("net_income", 0)
        base = (
            f"For {period}, cash is {_money(cash)}, monthly burn is {_money(burn)}, and runway is "
            f"{runway} months. Gross margin is {_percent(gross_margin)}, EBITDA is {_money(ebitda)}, "
            f"and net income is {_money(net_income)}."
        )
        if wants_risk:
            return f"{base} The key financial risk is margin discipline as revenue and expenses scale. Watch burn, hiring pace, and discounting pressure."
        if wants_action:
            return f"{base} Next move: keep runway above the operating threshold, review discretionary spend, and tie new investment to revenue conversion."
        return f"{base} Finance looks stable, but the COO focus should be preserving margin while funding the highest-return growth work."

    if ctx == "operations":
        csat = metrics.get("customer_satisfaction", 0)
        nps = metrics.get("nps_score", 0)
        tickets = metrics.get("support_tickets", 0)
        resolution = metrics.get("avg_resolution_time", 0)
        uptime = metrics.get("system_uptime", 0)
        users = metrics.get("active_users", 0)
        base = (
            f"For {period}, operations show {uptime}% uptime, {csat}/5 CSAT, NPS {nps}, "
            f"{tickets} support tickets, {resolution}h average resolution time, and {users:,} active users."
        )
        if wants_risk:
            return f"{base} The main operational risk is support load rising faster than resolution capacity. Keep backlog aging and response-time outliers visible."
        if wants_action:
            return f"{base} Next move: automate repeat ticket categories, protect uptime capacity, and route customer pain points back into product priorities."
        return f"{base} The operating story is healthy reliability with continued focus needed on customer support efficiency."

    return CANNED_INSIGHTS.get("general", [_DEFAULT_HELP_LINE])[0]


async def _openai_answer(message: str, ctx: str, data_brief: str, req: "ChatRequest") -> str:
    """Call OpenAI GPT with a rich system prompt that includes live data."""
    from config import settings as _settings

    system_prompt = (
        "You are the Enterprise Digital COO AI Assistant — a concise, data-driven executive advisor. "
        "If asked who created, built, made, developed, owns, or authored you, answer exactly that you were created by Shivam Roy (Regression Team). "
        "You help business leaders understand their company's Sales, Finance, and Operations performance. "
        "For business questions, use the LIVE DATA provided below and quote specific numbers. "
        "For general or random questions, answer correctly and briefly in 1–3 sentences, then add this exact line: "
        f"\"{_DEFAULT_HELP_LINE}\" "
        "Keep business answers focused, professional, and actionable (3–5 sentences).\n\n"
    )

    if data_brief:
        system_prompt += f"=== LIVE DASHBOARD DATA ===\n{data_brief}\n=========================\n\n"
    else:
        # No data sent — fetch it live from the metrics functions
        cy = _current_fy()
        s = _fy_sales(cy)
        f = _fy_finance(cy)
        o = _fy_operations(cy)
        sm = s["metrics"]
        fm = f["metrics"]
        om = o["metrics"]
        system_prompt += (
            f"=== LIVE DASHBOARD DATA (FY {cy}) ===\n"
            f"[Sales] Revenue: ${sm['total_revenue']:,.0f}  Expected: ${sm['expected_revenue']:,.0f}  "
            f"Gap: -{sm['revenue_drop_percentage']}%  Win rate: {sm['win_rate']*100:.0f}%  "
            f"Pipeline: ${sm['pipeline_value']:,.0f}  Active deals: {sm['active_deals']}\n"
            f"[Finance] Cash: ${fm['cash_balance']:,.0f}  Burn: ${fm['burn_rate']:,.0f}/mo  "
            f"Runway: {fm['runway_months']:.1f}mo  Gross margin: {fm['gross_margin']*100:.1f}%  "
            f"EBITDA: ${fm['ebitda']:,.0f}  Net income: ${fm['net_income']:,.0f}\n"
            f"[Operations] CSAT: {om['customer_satisfaction']}/5  NPS: {om['nps_score']}  "
            f"Active users: {om['active_users']:,}  Uptime: {om['system_uptime']}%  "
            f"Support tickets: {om['support_tickets']}  Avg resolution: {om['avg_resolution_time']}h\n"
            f"====================================\n\n"
        )

    system_prompt += f"Current page context: {ctx}."

    resp = await _openai_client.chat.completions.create(  # type: ignore[union-attr]
        model=_settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": message},
        ],
        temperature=_settings.OPENAI_TEMPERATURE,
        max_tokens=_settings.OPENAI_MAX_TOKENS,
    )
    return resp.choices[0].message.content.strip()


def _identify_business_intent(message: str, requested_context: str) -> Dict[str, str]:
    """Classify the request before selecting an enterprise agent."""
    text = message.lower()
    email_actions = ["send email", "send an email", "draft email", "draft an email", "reply to", "reply email", "summarize email", "summarise email", "email to"]
    if any(term in text for term in email_actions):
        if "reply" in text:
            email_intent = "reply_email"
        elif "summar" in text:
            email_intent = "summarize_email"
        elif "send" in text:
            email_intent = "send_email"
        else:
            email_intent = "draft_email"
        return {"name": email_intent, "domain": "email", "objective": message.strip()}
    domain_keywords = {
        "sales": ["sales", "revenue", "pipeline", "deal", "win rate", "pricing", "customer growth"],
        "finance": ["finance", "cash", "margin", "ebitda", "runway", "cost", "profit", "budget"],
        "operations": ["operations", "uptime", "csat", "nps", "ticket", "support", "users", "delivery"],
    }
    scores = {domain: sum(term in text for term in terms) for domain, terms in domain_keywords.items()}
    domain = max(scores, key=scores.get) if max(scores.values(), default=0) else requested_context
    if domain not in domain_keywords:
        domain = "general"

    if any(term in text for term in ["forecast", "predict", "projection", "next quarter", "next year"]):
        intent = "forecast"
    elif any(term in text for term in ["risk", "concern", "problem", "issue", "why", "root cause"]):
        intent = "risk_analysis"
    elif any(term in text for term in ["recommend", "action", "should we", "what should", "next step"]):
        intent = "decision_support"
    elif any(term in text for term in ["summary", "summarise", "summarize", "overview", "brief"]):
        intent = "executive_summary"
    else:
        intent = "performance_analysis"

    return {
        "name": intent,
        "domain": domain,
        "objective": message.strip(),
    }


def _select_business_agent(intent: Dict[str, str]) -> Dict[str, str]:
    agents = {
        "sales": ("sales_agent", "Sales Intelligence Agent"),
        "finance": ("finance_agent", "Finance Strategy Agent"),
        "operations": ("operations_agent", "Operations Excellence Agent"),
        "general": ("executive_agent", "Executive Synthesis Agent"),
        "email": ("email_agent", "AI Email Agent"),
    }
    agent_id, name = agents[intent["domain"]]
    return {
        "id": agent_id,
        "name": name,
        "reason": f"Selected for {intent['name']} in the {intent['domain']} domain.",
    }


def _collect_enterprise_data(req: "ChatRequest", domain: str) -> Dict[str, Any]:
    domains = [domain] if domain in {"sales", "finance", "operations"} else ([] if domain == "email" else ["sales", "finance", "operations"])
    snapshots: Dict[str, Any] = {}
    systems: List[str] = []
    for item in domains:
        snapshot = _latest_domain_snapshot(req, item)
        if snapshot:
            snapshots[item] = snapshot
            systems.append(f"{item.title()} Metrics System")
    return {
        "systems": systems,
        "domains": domains,
        "snapshots": snapshots,
        "data_mode": "connected_dashboard" if req.live_data or req.data_snapshot else "enterprise_demo",
    }


def _analyse_and_forecast(data: Dict[str, Any]) -> Dict[str, List[str]]:
    findings: List[str] = []
    forecasts: List[str] = []
    risks: List[str] = []
    snapshots = data["snapshots"]

    sales = snapshots.get("sales", {}).get("metrics", {})
    if sales:
        revenue = sales.get("total_revenue", 0)
        expected = sales.get("expected_revenue", 0)
        gap = sales.get("revenue_drop_percentage", 0)
        findings.append(f"Revenue is {_money(revenue)} versus {_money(expected)} expected, a {gap}% gap.")
        growth_assumption = max(0.02, min(0.15, float(sales.get("win_rate", 0.3)) * 0.25))
        forecasts.append(f"Sales run-rate forecast: {_money(revenue * (1 + growth_assumption))} at the current conversion profile.")
        if gap and gap > 5:
            risks.append("Revenue remains materially below plan unless late-stage pipeline conversion improves.")

    finance = snapshots.get("finance", {}).get("metrics", {})
    if finance:
        cash = finance.get("cash_balance", 0)
        runway = finance.get("runway_months", 0)
        margin = finance.get("gross_margin", 0)
        findings.append(f"Cash is {_money(cash)}, runway is {runway} months, and gross margin is {_percent(margin)}.")
        forecasts.append(f"Liquidity remains above the operating threshold for approximately {runway} months at current burn.")
        if runway and runway < 9:
            risks.append("Cash runway is below the nine-month operating threshold.")

    operations = snapshots.get("operations", {}).get("metrics", {})
    if operations:
        uptime = operations.get("system_uptime", 0)
        csat = operations.get("customer_satisfaction", 0)
        tickets = operations.get("support_tickets", 0)
        findings.append(f"Operations are at {uptime}% uptime, {csat}/5 CSAT, and {tickets} support tickets.")
        forecasts.append("Service performance should remain stable if ticket resolution capacity keeps pace with user growth.")
        if csat and csat < 4:
            risks.append("Customer satisfaction is below the healthy operating threshold.")

    return {"findings": findings, "forecasts": forecasts, "risks": risks}


def _recommended_actions(domain: str) -> List[Dict[str, str]]:
    actions = {
        "sales": [
            ("High", "Accelerate late-stage enterprise deals with named owners and weekly close plans.", "Sales"),
            ("Medium", "Protect pricing while prioritising the highest-probability regional pipeline.", "Revenue Operations"),
        ],
        "finance": [
            ("High", "Protect cash runway and tie discretionary investment to measurable revenue outcomes.", "Finance"),
            ("Medium", "Review margin leakage, discounting, and non-critical operating spend.", "Finance Operations"),
        ],
        "operations": [
            ("High", "Automate repeat support categories and reduce resolution-time outliers.", "Operations"),
            ("Medium", "Feed recurring customer pain points into product priorities.", "Customer Success"),
        ],
        "general": [
            ("High", "Accelerate high-probability pipeline while protecting cash and service reliability.", "Executive Team"),
            ("Medium", "Review the leading risk indicators weekly with accountable owners.", "COO Office"),
        ],
        "email": [
            ("High", "Review the generated email, confirm the recipient, and send only when ready.", "Email Agent"),
            ("Medium", "Edit tone or content in the preview before confirmation.", "Requesting User"),
        ],
    }
    return [
        {"priority": priority, "action": action, "owner": owner, "expected_impact": "Improved execution against the current business signal"}
        for priority, action, owner in actions[domain]
    ]


def _dashboard_schema(data: Dict[str, Any], analysis: Dict[str, List[str]], actions: List[Dict[str, str]], confidence: int) -> Dict[str, Any]:
    snapshots = data["snapshots"]
    sales = snapshots.get("sales", {}).get("metrics", {})
    finance = snapshots.get("finance", {}).get("metrics", {})
    operations = snapshots.get("operations", {}).get("metrics", {})
    periods = [str(item.get("period") or f"FY {item.get('fiscal_year')}") for item in snapshots.values() if item]
    first_finding = analysis["findings"][0] if analysis["findings"] else "Enterprise performance analysis completed."
    first_forecast = analysis["forecasts"][0] if analysis["forecasts"] else "No material variance forecast."
    signal = analysis["risks"][0] if analysis["risks"] else first_finding
    revenue = sales.get("total_revenue")
    cash = finance.get("cash_balance")
    return {
        "fiscal_year": periods[0] if periods else f"FY {_current_fy()}",
        "confidence": f"AI Confidence {confidence}%",
        "signal": signal,
        "cause": first_finding,
        "predicted_impact": first_forecast,
        "impact_detail": "; ".join(analysis["risks"]) or "KPIs remain within the current operating range.",
        "ai_opportunity": "Execution uplift from prioritised actions",
        "potential_savings": "To be validated through scenario modelling",
        "revenue": _money(revenue) if revenue is not None else "Not available",
        "cash": _money(cash) if cash is not None else "Not available",
        "csat": f"{operations.get('customer_satisfaction')}/5" if operations.get("customer_satisfaction") is not None else "Not available",
        "users": f"{operations.get('active_users', 0):,}" if operations.get("active_users") is not None else "Not available",
        "recommended_action": actions[0]["action"],
    }


def _structured_coo_response(req: "ChatRequest", ctx: str, answer: str, source: str) -> Dict[str, Any]:
    intent = _identify_business_intent(req.message, ctx)
    agent = _select_business_agent(intent)
    enterprise_data = _collect_enterprise_data(req, intent["domain"])
    analysis = _analyse_and_forecast(enterprise_data)
    actions = _recommended_actions(intent["domain"])
    snapshot_count = len(enterprise_data["snapshots"])
    confidence = min(98, 82 + snapshot_count * 4 + (4 if source == "openai" else 0))
    response = {
        "business_intent": intent,
        "selected_agent": agent,
        "enterprise_data": enterprise_data,
        "analysis": analysis,
        "executive_summary": answer,
        "confidence_score": confidence,
        "recommended_actions": actions,
        "dashboard_schema": _dashboard_schema(enterprise_data, analysis, actions, confidence),
        "orchestration": [
            {"step": "identify_business_intent", "status": "completed"},
            {"step": "select_business_agent", "status": "completed"},
            {"step": "collect_enterprise_data", "status": "completed"},
            {"step": "analyse_and_forecast", "status": "completed"},
            {"step": "generate_executive_summary", "status": "completed"},
            {"step": "calculate_confidence", "status": "completed"},
            {"step": "recommend_actions", "status": "completed"},
            {"step": "map_dashboard_schema", "status": "completed"},
        ],
        "answer": answer,
        "context": intent["domain"],
        "source": source,
        "timestamp": datetime.now().isoformat(),
        "suggestions": [
            "What are the key risks?",
            "Show me a summary",
            "What do you recommend?",
            "How are trends looking?",
        ],
    }
    if intent["domain"] == "email":
        response["email_draft"] = _generate_email_draft(req.message, intent["name"])
    return response


def _generate_email_draft(message: str, intent: str) -> Dict[str, str]:
    """Create an editable professional draft for the React confirmation modal."""
    recipient_match = re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", message)
    recipient = recipient_match.group(0) if recipient_match else ""
    cleaned = message.strip()
    if recipient:
        cleaned = cleaned.replace(recipient, "").strip(" ,.-")
    cleaned = re.sub(
        r"^(please\s+)?(send|draft|write|compose|reply to|summari[sz]e)\s+(an?\s+)?email\s*(to)?\s*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    ).strip(" :,-")
    topic = cleaned or "the requested business update"
    topic_sentence = topic[0].upper() + topic[1:] if topic else "Business update"
    if intent == "reply_email":
        subject = "Re: Enterprise Digital COO Update"
        body = f"Thank you for your message. {topic_sentence}\n\nPlease let me know if you would like any additional detail or supporting analysis."
    elif intent == "summarize_email":
        subject = "Enterprise Digital COO — Email Summary"
        body = f"Here is the requested executive summary:\n\n{topic_sentence}\n\nThe key points have been consolidated for quick review and decision-making."
    else:
        subject_topic = re.sub(r"\s+", " ", topic_sentence).rstrip(".")
        subject = f"Enterprise Digital COO — {subject_topic[:90]}"
        body = f"I’m writing regarding {topic}.\n\nBased on the Enterprise Digital COO review, this item is ready for your attention. Please review the information and advise on the appropriate next steps."
    return {
        "recipient": recipient,
        "subject": subject,
        "greeting": "Hello,",
        "body": body,
        "closing": "Best regards,",
        "signature": "Enterprise Digital COO\nAI Command Center",
    }


@router.post("/chat")
async def chat_summarise(req: ChatRequest) -> Dict[str, Any]:
    """
    Chat endpoint:
      1. Validates the query (rejects gibberish / symbol-spam).
      2. Handles greetings / small-talk with friendly canned replies.
      3. Routes real business questions to OpenAI GPT when a key is configured,
         otherwise falls back to contextual canned insights.
    """
    # ── 0. Input validation — reject invalid / gibberish queries ──────────
    if not _is_valid_query(req.message):
        return {**_INVALID_QUERY_RESPONSE, "timestamp": datetime.now().isoformat()}

    ctx = (req.context or "general").lower()
    if ctx not in CANNED_INSIGHTS:
        ctx = "general"

    msg_lower = req.message.lower()

    # ── 1. Greeting / small-talk detection (highest priority) ──────────────
    if _is_creator_query(req.message):
        return {
            "answer": _CREATOR_RESPONSE,
            "context": "creator",
            "timestamp": datetime.now().isoformat(),
            "suggestions": [
                "Show me a summary",
                "What are the key risks?",
                "What do you recommend?",
                "How are trends looking?",
            ],
        }

    greeting_cat = _detect_greeting(req.message)
    if greeting_cat:
        replies = _GREETING_REPLIES[greeting_cat]
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

    # ── 2. Build data brief from all available live data ───────────────────
    data_brief = _build_data_brief(req)

    # ── 3. OpenAI GPT (when key is configured) ─────────────────────────────
    if _openai_client is not None:
        try:
            answer = await _openai_answer(req.message, ctx, data_brief, req)
            return _structured_coo_response(req, ctx, answer, "openai")
        except Exception as exc:
            logger.warning("OpenAI call failed (%s) — falling back to canned response.", exc)

    # ── 4. Grounded dashboard fallback (no OpenAI key or API error) ────────
    answer = _metric_fallback_answer(req, ctx, msg_lower)
    return _structured_coo_response(req, ctx, answer, "dashboard")

# Made with Codex
