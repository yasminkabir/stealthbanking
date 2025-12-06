from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from typing import List, Dict, Any, Optional, Set
import os
import re
import asyncio
import csv
import io
import json
import hashlib
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import asyncpraw
from rapidfuzz import fuzz
from contextlib import asynccontextmanager

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.reddit = asyncpraw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT", "bank-feature-scraper/0.1"),
    )
    try:
        yield
    finally:
        await app.state.reddit.close()

app = FastAPI(title="Reddit Scraper API", version="0.1.0", lifespan=lifespan)

# Enable CORS for local dev and Flutter web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Bank detection (strict lexicon) ----------
# Multi-word bank names (exact phrase, word bounded)
BANK_PHRASES: Set[str] = {
    "ally bank", "bank of america", "wells fargo", "capital one", "td bank",
    "us bank", "fifth third", "bank of the west", "citizens bank", "pnc bank",
    "hsbc bank", "santander bank", "barclays bank", "standard chartered",
    "american express", "bank of scotland", "royal bank of canada",
    "bank of montreal", "state bank of india", "icici bank", "axis bank",
    "union bank", "first republic", "first citizens", "credit suisse",
    "deutsche bank", "jpmorgan chase", "jp morgan", "morgan stanley",
}

# Single-word brands (must appear as a whole word; some are ambiguous)
SINGLE_WORD_BANKS: Set[str] = {
    "chase", "citi", "citibank", "pnc", "hsbc", "barclays", "santander",
    "monzo", "revolut", "nubank", "sofi", "chime", "wise", "ally",
}

# Tokens that require context (e.g., 'ally' vs 'finally')
AMBIGUOUS: Set[str] = {"ally"}

WORD_RE = re.compile(r"\b[a-z][a-z&.\-']*\b", re.IGNORECASE)

def _words(text: str) -> List[str]:
    return [w.lower() for w in WORD_RE.findall(text or "")]

def _has_phrase(text: str, phrase: str) -> bool:
    return re.search(rf"\b{re.escape(phrase)}\b", text or "", flags=re.IGNORECASE) is not None

def _within_window(tokens: List[str], i: int, ctx: Set[str], k: int = 3) -> bool:
    lo, hi = max(0, i - k), min(len(tokens), i + k + 1)
    window = tokens[lo:hi]
    return any(t in ctx for t in window)

def extract_banks(text: str) -> List[str]:
    if not text:
        return []
    t = text.lower()
    hits: Set[str] = set()
    # 1) Phrases
    for phrase in BANK_PHRASES:
        if _has_phrase(t, phrase):
            hits.add(phrase)
    # 2) Whole-word singles with ambiguity guards
    tokens = _words(t)
    token_set = set(tokens)
    for brand in SINGLE_WORD_BANKS:
        if brand not in token_set:
            continue
        if brand in AMBIGUOUS:
            if any(_within_window(tokens, i, {"bank", "banking", "app", "card", "checking", "savings"})
                   for i, tok in enumerate(tokens) if tok == brand):
                if _has_phrase(t, "ally bank"):
                    hits.add("ally bank")
                else:
                    # Only emit "ally" if explicitly near banking context
                    hits.add("ally")
        else:
            hits.add(brand)
    # 3) Canonicalize
    canon_map = {
        "jp morgan": "jpmorgan chase",
        "citibank": "citi",
        "pnc bank": "pnc",
        "hsbc bank": "hsbc",
        "barclays bank": "barclays",
        "santander bank": "santander",
        "us bank": "us bank",
    }
    normalized = set(canon_map.get(h, h) for h in hits)
    # 4) Safety removals (non-banks)
    normalized -= {"zelle", "venmo", "cash app", "apple pay", "google pay"}
    return sorted(normalized)

def mentions_bank(text: str) -> bool:
    return bool(extract_banks(text))


# ---------- Feature extraction ----------
# A compact taxonomy -> keywords/regex lists.
FEATURE_MAP = {
    "login_auth": [
        r"\blogin\b", r"\bsign[- ]?in\b", r"\b2fa\b", r"\bmfa\b",
        r"\bone[- ]?time[- ]?pass(code|word)?\b", r"\botp\b",
        r"\bbiometric(s)?\b", r"\bface[- ]?id\b", r"\btouch[- ]?id\b",
    ],
    "payments_transfers": [
        r"\btransfer(s|ring)?\b", r"\bzelle\b", r"\bwire\b",
        r"\bpay(ment|ments)?\b", r"\bbill[- ]?pay\b", r"\bvenmo\b", r"\bcash app\b",
    ],
    "cards_controls": [
        r"\bvirtual (card|cards)\b", r"\bfreeze (card|my card)\b",
        r"\block (card|my card)\b", r"\bunfreeze\b", r"\bcard controls?\b",
    ],
    "check_deposit": [
        r"\bmobile (check )?deposit\b", r"\bremote deposit\b", r"\bphoto deposit\b",
    ],
    "balances_statements": [
        r"\bbalance(s)?\b", r"\bstatement(s)?\b", r"\btransaction(s)?\b",
        r"\bspending\b", r"\bcategory\b", r"\bexport\b", r"\bdownload\b",
    ],
    "budgeting_analytics": [
        r"\bbudget(ing)?\b", r"\bsavings? goal(s)?\b", r"\binsight(s)?\b", r"\bchart(s)?\b",
    ],
    "notifications": [
        r"\bnotification(s)?\b", r"\bpush\b", r"\balert(s)?\b",
    ],
    "profile_settings": [
        r"\bprofile\b", r"\bsettings?\b", r"\baddress\b", r"\bemail\b", r"\bphone\b", r"\bpassword\b",
    ],
    "security_fraud": [
        r"\bfraud\b", r"\bdispute(s|d)?\b", r"\bchargeback\b", r"\bfreeze\b", r"\block(ed)?\b",
    ],
    "support_chat": [
        r"\bchat support\b", r"\blive chat\b", r"\bsupport\b", r"\bcontact\b", r"\bhelp\b",
    ],
    "rewards_offers": [
        r"\breward(s)?\b", r"\bcashback\b", r"\boffer(s)?\b", r"\bpoints\b",
    ],
    "wallet_integrations": [
        r"\bapple pay\b", r"\bgoogle pay\b", r"\bwallet\b",
    ],
    "ui_ux_accessibility": [
        r"\bdark mode\b", r"\baccessibility\b", r"\bfont size\b", r"\blayout\b", r"\bnavigation\b", r"\bcrash(ed|es|ing)?\b", r"\bbug(s)?\b", r"\bslow\b",
    ],
}

FEATURE_COMPILED = {k: [re.compile(p, re.IGNORECASE) for p in v] for k, v in FEATURE_MAP.items()}

PLATFORM_REGEX = re.compile(r"\b(iOS|Android)\b", re.IGNORECASE)
VERSION_REGEX = re.compile(r"\b(v|version)?\s?\d+\.\d+(\.\d+)?\b", re.IGNORECASE)


def extract_features(text: str) -> List[str]:
    tags = set()
    t = text or ""
    for tag, patterns in FEATURE_COMPILED.items():
        if any(p.search(t) for p in patterns):
            tags.add(tag)
    return sorted(tags)


def extract_platform_version(text: str) -> Dict[str, Optional[str]]:
    t = text or ""
    platform: Optional[str] = None
    m_platform = PLATFORM_REGEX.search(t)
    if m_platform:
        platform = m_platform.group(0)

    version: Optional[str] = None
    m_ver = VERSION_REGEX.search(t)
    if m_ver:
        version = m_ver.group(0).replace("version", "").strip()
    return {"platform_hint": platform, "version_hint": version}


# ---------- PII redaction ----------
PII_PATTERNS = [
    re.compile(r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b"),  # credit card-like
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),                    # SSN-ish
    re.compile(r"\b\d{9,18}\b"),                             # long numeric sequences (acct nos)
    re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),  # emails
    re.compile(r"\b\+?\d{7,15}\b"),                         # phone-like
]


def redact(text: str) -> str:
    redacted = text or ""
    for patt in PII_PATTERNS:
        redacted = patt.sub("[REDACTED_PII]", redacted)
    return redacted


# ---------- Issue Detection ----------
ISSUE_TERMS = [
    r"\blogin\b", r"\blog\s+in\b", r"\bsign\s+in\b", r"\b2fa\b", r"\bmfa\b", r"\botp\b",
    r"\bbiometric\b", r"\bface\s+id\b", r"\btouch\s+id\b",
    r"\berror\b", r"\bfailed\b", r"\bdenied\b", r"\bdeclined\b", r"\brejected\b", r"\bblocked\b", r"\blocked\b", r"\bfreeze\b", r"\bfraud\b",
    r"\bdeposit\b", r"\bmobile\s+deposit\b", r"\bcheck\s+deposit\b", r"\btransfer\b", r"\bzelle\b", r"\bwire\b", r"\bbill\s+pay\b",
    r"\bchargeback\b", r"\bdispute\b", r"\bvirtual\s+card\b", r"\bfreeze\s+card\b", r"\bunfreeze\b",
    r"\bcrash\b", r"\bcrashing\b", r"\bbug\b", r"\bslow\b", r"\blag\b", r"\bhang\b", r"\bstuck\b",
    r"\bverification\b", r"\bkyc\b", r"\baddress\s+update\b", r"\bprofile\b", r"\bpassword\s+reset\b",
]
ISSUE_REGEX = re.compile("|".join(ISSUE_TERMS), re.IGNORECASE)

def is_issue_like(text: str) -> bool:
    return bool(ISSUE_REGEX.search(text or ""))


# ---------- Enhanced Sentiment Analysis ----------
POSITIVE_TERMS = [
    r"\bexcellent\b", r"\bgreat\b", r"\bamazing\b", r"\bperfect\b", r"\blove\b", r"\bfantastic\b",
    r"\bwonderful\b", r"\boutstanding\b", r"\bsmooth\b", r"\beasy\b", r"\bquick\b", r"\bfast\b",
    r"\bhelpful\b", r"\bsupportive\b", r"\bresponsive\b", r"\bprofessional\b", r"\breliable\b"
]

NEGATIVE_TERMS = [
    r"\bterrible\b", r"\bawful\b", r"\bhorrible\b", r"\bworst\b", r"\bhate\b", r"\bdisgusting\b",
    r"\bfrustrating\b", r"\bannoying\b", r"\bdisappointing\b", r"\bpathetic\b", r"\bunacceptable\b",
    r"\bnightmare\b", r"\bdisaster\b", r"\bscam\b", r"\bfraud\b", r"\bsteal\b", r"\bcheat\b"
]

POSITIVE_REGEX = re.compile("|".join(POSITIVE_TERMS), re.IGNORECASE)
NEGATIVE_REGEX = re.compile("|".join(NEGATIVE_TERMS), re.IGNORECASE)

def analyze_sentiment(text: str) -> tuple[str, float]:
    """Returns (sentiment_label, sentiment_score)"""
    text_lower = (text or "").lower()
    
    # Count positive and negative terms
    pos_count = len(POSITIVE_REGEX.findall(text_lower))
    neg_count = len(NEGATIVE_REGEX.findall(text_lower))
    
    # Check for issue terms (strong negative indicator)
    is_issue = bool(ISSUE_REGEX.search(text_lower))
    
    # Calculate sentiment score (-1 to 1)
    if is_issue and neg_count > 0:
        sentiment_score = -0.8  # Strong negative for issues
        sentiment_label = "negative"
    elif is_issue:
        sentiment_score = -0.5  # Moderate negative for issues
        sentiment_label = "negative"
    elif pos_count > neg_count:
        sentiment_score = 0.6   # Positive
        sentiment_label = "positive"
    elif neg_count > pos_count:
        sentiment_score = -0.3  # Negative
        sentiment_label = "negative"
    else:
        sentiment_score = 0.0   # Neutral
        sentiment_label = "neutral"
    
    return sentiment_label, sentiment_score


# ---------- Topic Classification ----------
TOPIC_PATTERNS = {
    "login_auth": [r"\blogin\b", r"\bsign\s+in\b", r"\b2fa\b", r"\bmfa\b", r"\bbiometric\b", r"\bpassword\b"],
    "payments": [r"\btransfer\b", r"\bpayment\b", r"\bbill\s+pay\b", r"\bzelle\b", r"\bwire\b", r"\bdeposit\b"],
    "cards": [r"\bcard\b", r"\bcredit\s+card\b", r"\bdebit\s+card\b", r"\bvirtual\s+card\b", r"\bfreeze\s+card\b"],
    "mobile_app": [r"\bapp\b", r"\bmobile\b", r"\bcrash\b", r"\bbug\b", r"\bslow\b", r"\bupdate\b"],
    "fees": [r"\bfee\b", r"\bcharge\b", r"\bcost\b", r"\bexpensive\b", r"\boverdraft\b"],
    "customer_service": [r"\bsupport\b", r"\bhelp\b", r"\bcontact\b", r"\bchat\b", r"\bcall\b", r"\bphone\b"],
    "security": [r"\bfraud\b", r"\bscam\b", r"\bsecurity\b", r"\bhack\b", r"\bbreach\b", r"\bsteal\b"],
    "account_management": [r"\baccount\b", r"\bprofile\b", r"\bsettings\b", r"\bclose\b", r"\bopen\b", r"\bverify\b"]
}

def classify_topic(text: str) -> str:
    """Classify the main topic of the text"""
    text_lower = (text or "").lower()
    topic_scores = {}
    
    for topic, patterns in TOPIC_PATTERNS.items():
        score = sum(len(re.findall(pattern, text_lower, re.IGNORECASE)) for pattern in patterns)
        topic_scores[topic] = score
    
    # Return the topic with highest score, or "general" if no matches
    if topic_scores and max(topic_scores.values()) > 0:
        return max(topic_scores, key=topic_scores.get)
    else:
        return "general"


# ---------- Quality Filtering ----------
def keep_by_quality(score: int, num_comments: int, min_score: int = 5, min_comments: int = 5) -> bool:
    return score >= min_score and num_comments >= min_comments


# ---------- Data Storage and Deduplication ----------
DATA_FILE = Path("scraped_data.json")
SEEN_HASHES_FILE = Path("seen_posts.json")
FAKE_LLM_DATA_FILE = Path(__file__).parent / "app" / "fake_llm_data.json"

def load_existing_data() -> List[Dict[str, Any]]:
    """Load existing scraped data from file"""
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    return []

def load_seen_hashes() -> Set[str]:
    """Load hashes of posts we've already seen"""
    if SEEN_HASHES_FILE.exists():
        try:
            with open(SEEN_HASHES_FILE, 'r', encoding='utf-8') as f:
                return set(json.load(f))
        except (json.JSONDecodeError, FileNotFoundError):
            return set()
    return set()

def save_data(data: List[Dict[str, Any]]) -> None:
    """Save scraped data to file"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def save_seen_hashes(hashes: Set[str]) -> None:
    """Save seen post hashes to file"""
    with open(SEEN_HASHES_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(hashes), f, indent=2)


def load_fake_llm_data() -> Dict[str, Any]:
    """
    Load the synthetic LLM banking insights data used for front-end mocks.
    """
    if not FAKE_LLM_DATA_FILE.exists():
        raise FileNotFoundError(f"LLM data file not found at {FAKE_LLM_DATA_FILE}")
    with open(FAKE_LLM_DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_post_hash(post_id: str, bank_name: str, text_snippet: str) -> str:
    """Generate a unique hash for a post-bank combination to detect duplicates"""
    content = f"{post_id}_{bank_name}_{text_snippet[:100]}"  # Use first 100 chars of text
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def is_duplicate(post_hash: str, seen_hashes: Set[str]) -> bool:
    """Check if we've already processed this post-bank combination"""
    return post_hash in seen_hashes


# ---------- Routes ----------
@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


async def _fetch_posts(reddit_client: asyncpraw.Reddit, subreddit: str, sort: str, limit: int, time_filter: Optional[str]):
    sub = await reddit_client.subreddit(subreddit)
    if sort == "hot":
        return sub.hot(limit=limit)
    if sort == "new":
        return sub.new(limit=limit)
    if sort == "rising":
        return sub.rising(limit=limit)
    # top
    tf = time_filter or "day"
    return sub.top(time_filter=tf, limit=limit)


@app.get("/reddit/{subreddit}/features")
async def reddit_features(
    subreddit: str,
    sort: str = Query("hot", pattern=r"^(hot|new|top|rising)$"),
    limit: int = Query(20, ge=1, le=100),
    time_filter: Optional[str] = Query("day", description="Used only when sort=top"),
    include_comments: bool = Query(False),
) -> Dict[str, Any]:
    try:
        reddit_client = app.state.reddit
        post_iter = await _fetch_posts(reddit_client, subreddit, sort, limit, time_filter)
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Failed to initialize subreddit") from exc

    items: List[Dict[str, Any]] = []

    try:
        async for submission in post_iter:
            text = f"{submission.title or ''}\n{submission.selftext or ''}"
            if not mentions_bank(text):
                continue

            banks = extract_banks(text)
            features = extract_features(text)
            hints = extract_platform_version(text)
            clean_text = redact(text)

            item: Dict[str, Any] = {
                "id": submission.id,
                "title": redact(submission.title or ""),
                "created_utc": submission.created_utc,
                "score": getattr(submission, "score", None),
                "num_comments": getattr(submission, "num_comments", None),
                "permalink": f"https://www.reddit.com{submission.permalink}",
                "url": getattr(submission, "url", None),
                "banks": banks,
                "features": features,
                **hints,
                "text_redacted": clean_text,
            }

            if include_comments:
                try:
                    await submission.load()
                    await submission.comments.replace_more(limit=0)
                    top_level = list(submission.comments)
                    comment_items: List[Dict[str, Any]] = []
                    for c in top_level[:50]:
                        body = getattr(c, "body", None)
                        if not isinstance(body, str):
                            continue
                        if not mentions_bank(body):
                            continue
                        c_banks = extract_banks(body)
                        c_features = extract_features(body)
                        c_hints = extract_platform_version(body)
                        comment_items.append(
                            {
                                "id": getattr(c, "id", None),
                                "text_redacted": redact(body),
                                "banks": c_banks,
                                "features": c_features,
                                **c_hints,
                            }
                        )
                    item["comments"] = comment_items
                except Exception:
                    # If comment fetch fails, proceed without comments
                    item["comments"] = []

            items.append(item)
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Failed to fetch posts") from exc

    return {
        "subreddit": subreddit,
        "count": len(items),
        "items": items,
        "params": {"sort": sort, "limit": limit, "time_filter": time_filter, "include_comments": include_comments},
    }


@app.get("/llm/banking-insights")
def get_banking_insights() -> Dict[str, Any]:
    """
    Serve synthetic LLM-generated banking insights for front-end visualization mocks.
    """
    try:
        return load_fake_llm_data()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=500, detail="Failed to parse LLM data file") from exc


@app.get("/debug/detect")
async def debug_detect(text: str = Query(..., description="Text to analyze")) -> Dict[str, Any]:
    banks = extract_banks(text)
    is_issue = is_issue_like(text)
    redacted = redact(text)
    return {
        "text": text,
        "redacted": redacted,
        "banks_detected": banks,
        "is_issue": is_issue,
    }


@app.get("/reddit/ml-data")
async def reddit_ml_data(
    subs: str = Query("personalfinance+Banking+CreditCards+Chimebank+Revolut+Monzo", description="Subreddits separated by +"),
    sort: str = Query("hot", pattern=r"^(hot|new|top|rising)$"),
    fetch_limit: int = Query(200, ge=10, le=500),
    min_score: int = Query(5),
    min_comments: int = Query(5),
    time_filter: Optional[str] = Query("day", description="Used only when sort=top"),
    format: str = Query("json", description="Output format: json or csv"),
    append: bool = Query(True, description="Append to existing data file"),
) -> Any:
    """Returns data in ML pipeline format: index, platform, bank_name, post_text, category, sentiment_label, sentiment_score, date, user_followers, likes, shares, replies, language, source_url"""
    
    # Load existing data and seen hashes
    existing_data = load_existing_data() if append else []
    seen_hashes = load_seen_hashes()
    
    subreddit_list = [s.strip() for s in subs.split("+")]
    new_data = []
    new_hashes = set()
    index = len(existing_data)  # Continue indexing from existing data
    
    for subreddit in subreddit_list:
        try:
            reddit_client = app.state.reddit
            post_iter = await _fetch_posts(reddit_client, subreddit, sort, fetch_limit, time_filter)
        except Exception as exc:
            continue  # Skip failed subreddits

        try:
            async for submission in post_iter:
                # Quality filter
                score = getattr(submission, "score", 0) or 0
                num_comments = getattr(submission, "num_comments", 0) or 0
                if not keep_by_quality(score, num_comments, min_score, min_comments):
                    continue

                text = f"{submission.title or ''}\n{submission.selftext or ''}"
                banks = extract_banks(text)
                if not banks:
                    continue

                is_issue = is_issue_like(text)
                features = extract_features(text)
                platform_hint = extract_platform_version(text).get("platform_hint", "unknown")
                
                # Enhanced sentiment and topic analysis
                sentiment_label, sentiment_score = analyze_sentiment(text)
                topic = classify_topic(text)
                
                # Convert timestamp to readable date
                created_date = datetime.fromtimestamp(submission.created_utc).strftime("%Y-%m-%d %H:%M:%S")
                
                # Create one row per bank mentioned
                for bank in banks:
                    # Generate hash for deduplication
                    post_hash = generate_post_hash(submission.id, bank, text)
                    
                    # Skip if we've already seen this post-bank combination
                    if is_duplicate(post_hash, seen_hashes):
                        continue
                    
                    # Add to new data
                    new_data.append({
                        "index": index,
                        "platform": platform_hint.lower() if platform_hint else "unknown",
                        "bank_name": bank,
                        "post_text": redact(text),
                        "category": topic,  # Now using detailed topic classification
                        "sentiment_label": sentiment_label,  # Enhanced sentiment analysis
                        "sentiment_score": sentiment_score,  # More nuanced scoring
                        "date": created_date,
                        "user_followers": 0,  # Reddit doesn't provide this easily
                        "likes": score,
                        "shares": 0,  # Reddit doesn't have shares
                        "replies": num_comments,
                        "language": "en",  # Assume English for now
                        "source_url": f"https://www.reddit.com{submission.permalink}",
                        "post_id": submission.id,  # Add for tracking
                        "hash": post_hash  # Add for deduplication tracking
                    })
                    
                    # Track this as seen
                    new_hashes.add(post_hash)
                    seen_hashes.add(post_hash)
                    index += 1

        except Exception:
            continue  # Skip failed subreddits

    # Save new data and hashes
    if new_data:
        all_data = existing_data + new_data
        save_data(all_data)
        save_seen_hashes(seen_hashes)

    if format.lower() == "csv":
        # Return CSV format (all data or just new data based on append)
        output_data = all_data if append else new_data
        output = io.StringIO()
        if output_data:
            writer = csv.DictWriter(output, fieldnames=output_data[0].keys())
            writer.writeheader()
            writer.writerows(output_data)
        return PlainTextResponse(content=output.getvalue(), media_type="text/csv")
    else:
        # Return JSON format
        return {
            "new_data": new_data,
            "total_new_records": len(new_data),
            "total_all_records": len(existing_data) + len(new_data),
            "subreddits": subreddit_list,
            "duplicates_skipped": len(seen_hashes) - len(new_hashes),
            "params": {
                "sort": sort, "fetch_limit": fetch_limit, "min_score": min_score, 
                "min_comments": min_comments, "time_filter": time_filter, "append": append
            }
        }


@app.get("/data/status")
def data_status() -> Dict[str, Any]:
    """Get status of stored data"""
    existing_data = load_existing_data()
    seen_hashes = load_seen_hashes()
    
    return {
        "total_records": len(existing_data),
        "unique_post_bank_combinations": len(seen_hashes),
        "data_file_exists": DATA_FILE.exists(),
        "seen_hashes_file_exists": SEEN_HASHES_FILE.exists(),
        "data_file_size": DATA_FILE.stat().st_size if DATA_FILE.exists() else 0,
        "seen_hashes_file_size": SEEN_HASHES_FILE.stat().st_size if SEEN_HASHES_FILE.exists() else 0,
    }

@app.delete("/data/clear")
def clear_data() -> Dict[str, str]:
    """Clear all stored data"""
    if DATA_FILE.exists():
        DATA_FILE.unlink()
    if SEEN_HASHES_FILE.exists():
        SEEN_HASHES_FILE.unlink()
    
    return {"message": "All data cleared successfully"}

@app.get("/data/export")
def export_data(format: str = Query("json", description="Export format: json or csv")) -> Any:
    """Export all stored data"""
    existing_data = load_existing_data()
    
    if not existing_data:
        return {"message": "No data to export"}
    
    if format.lower() == "csv":
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=existing_data[0].keys())
        writer.writeheader()
        writer.writerows(existing_data)
        return PlainTextResponse(content=output.getvalue(), media_type="text/csv")
    else:
        return {
            "data": existing_data,
            "total_records": len(existing_data),
            "exported_at": datetime.now().isoformat()
        }

@app.get("/")
def root() -> Dict[str, Any]:
    return {
        "name": "Reddit Scraper API",
        "version": "0.1.0",
        "endpoints": [
            {"GET": "/health"},
            {"GET": "/reddit/{subreddit}/features"},
            {"GET": "/debug/detect"},
            {"GET": "/reddit/{subreddit}/banks"},
            {"GET": "/reddit/banks"},
            {"GET": "/llm/banking-insights"},
            {"GET": "/reddit/ml-data"},
            {"GET": "/data/status"},
            {"GET": "/data/export"},
            {"DELETE": "/data/clear"},
        ],
    }


@app.get("/reddit/{subreddit}/banks")
async def reddit_banks(
    subreddit: str,
    sort: str = Query("hot", pattern=r"^(hot|new|top|rising)$"),
    fetch_limit: int = Query(200, ge=10, le=500, description="How many posts to scan"),
    per_bank_limit: int = Query(10, ge=1, le=50, description="Max posts to return per bank"),
    time_filter: Optional[str] = Query("day", description="Used only when sort=top"),
) -> Dict[str, Any]:
    try:
        reddit_client = app.state.reddit
        # correct argument order: (client, subreddit, sort, limit, time_filter)
        post_iter = await _fetch_posts(reddit_client, subreddit, sort, fetch_limit, time_filter)
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Failed to initialize subreddit") from exc

    grouped: Dict[str, List[Dict[str, Any]]] = {}

    try:
        async for submission in post_iter:
            text = f"{submission.title or ''}\n{submission.selftext or ''}"
            banks = extract_banks(text)
            if not banks:
                continue
            post_info = {
                "id": submission.id,
                "title": redact(submission.title or ""),
                "created_utc": submission.created_utc,
                "score": getattr(submission, "score", None),
                "num_comments": getattr(submission, "num_comments", None),
                "permalink": f"https://www.reddit.com{submission.permalink}",
                "url": getattr(submission, "url", None),
            }
            for bank in banks:
                lst = grouped.setdefault(bank, [])
                if len(lst) < per_bank_limit:
                    lst.append(post_info)

            # Stop early if all known banks hit per-bank cap (optional)
            if all(len(v) >= per_bank_limit for v in grouped.values()) and len(grouped) >= 1:
                # We have at least one bank and all filled to cap; continue scanning for diversity? keep simple: break
                pass
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Failed to fetch posts") from exc

    return {
        "subreddit": subreddit,
        "params": {"sort": sort, "fetch_limit": fetch_limit, "per_bank_limit": per_bank_limit, "time_filter": time_filter},
        "found_banks": sorted(grouped.keys()),
        "banks": grouped,
    }


@app.get("/reddit/banks")
async def reddit_banks_multi(
    subs: str = Query("personalfinance+Banking+CreditCards+Chimebank+Revolut+Monzo", description="Subreddits separated by +"),
    sort: str = Query("hot", pattern=r"^(hot|new|top|rising)$"),
    fetch_limit: int = Query(200, ge=10, le=500),
    per_bank_limit: int = Query(10, ge=1, le=50),
    include_comments: bool = Query(True),
    issue_only: bool = Query(True),
    min_score: int = Query(5),
    min_comments: int = Query(5),
    time_filter: Optional[str] = Query("day", description="Used only when sort=top"),
    format: str = Query("json", description="Output format: json or csv"),
) -> Dict[str, Any]:
    subreddit_list = [s.strip() for s in subs.split("+")]
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    
    for subreddit in subreddit_list:
        try:
            reddit_client = app.state.reddit
            post_iter = await _fetch_posts(reddit_client, subreddit, sort, fetch_limit, time_filter)
        except Exception as exc:
            continue  # Skip failed subreddits

        try:
            async for submission in post_iter:
                # Quality filter
                score = getattr(submission, "score", 0) or 0
                num_comments = getattr(submission, "num_comments", 0) or 0
                if not keep_by_quality(score, num_comments, min_score, min_comments):
                    continue

                text = f"{submission.title or ''}\n{submission.selftext or ''}"
                banks = extract_banks(text)
                if not banks:
                    continue

                is_issue = is_issue_like(text)
                if issue_only and not is_issue:
                    continue

                # Process comments if requested
                comments = []
                if include_comments:
                    try:
                        await submission.load()
                        await submission.comments.replace_more(limit=0)
                        top_level = list(submission.comments)
                        for c in top_level[:50]:
                            body = getattr(c, "body", None)
                            if not isinstance(body, str):
                                continue
                            c_banks = extract_banks(body)
                            if not c_banks:
                                continue
                            c_is_issue = is_issue_like(body)
                            if issue_only and not c_is_issue:
                                continue
                            comments.append({
                                "id": getattr(c, "id", None),
                                "body": redact(body),
                                "banks_detected": c_banks,
                                "is_issue": c_is_issue,
                            })
                    except Exception:
                        pass

                post_info = {
                    "id": submission.id,
                    "title": redact(submission.title or ""),
                    "created_utc": submission.created_utc,
                    "score": score,
                    "num_comments": num_comments,
                    "permalink": f"https://www.reddit.com{submission.permalink}",
                    "url": getattr(submission, "url", None),
                    "banks_detected": banks,
                    "is_issue": is_issue,
                    "text_redacted": redact(text),
                    "comments": comments,
                }

                for bank in banks:
                    lst = grouped.setdefault(bank, [])
                    if len(lst) < per_bank_limit:
                        lst.append(post_info)

        except Exception:
            continue  # Skip failed subreddits

    return {
        "subreddits": subreddit_list,
        "params": {
            "sort": sort, "fetch_limit": fetch_limit, "per_bank_limit": per_bank_limit,
            "include_comments": include_comments, "issue_only": issue_only,
            "min_score": min_score, "min_comments": min_comments, "time_filter": time_filter
        },
        "found_banks": sorted(grouped.keys()),
        "banks": grouped,
    }


