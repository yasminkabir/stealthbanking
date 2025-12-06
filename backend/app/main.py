from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional

from .scraper import fetch_subreddit_posts
from .chatbot import chat_with_context


class RedditPost(BaseModel):
    id: str = Field(..., description="Reddit post id")
    title: str
    author: Optional[str] = None
    score: int
    num_comments: int
    created_utc: float
    url: Optional[str] = None
    permalink: str
    subreddit: str
    thumbnail: Optional[str] = None


class PostsResponse(BaseModel):
    subreddit: str
    sort: str
    time_filter: Optional[str] = None
    limit: int
    posts: List[RedditPost]


class ChatRequest(BaseModel):
    message: str = Field(..., description="User's chat message")


class ChatResponse(BaseModel):
    response: str = Field(..., description="Chatbot's response")


app = FastAPI(title="Reddit Scraper API", version="0.1.0")

# Enable CORS for local dev and Flutter web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/reddit/{subreddit}", response_model=PostsResponse)
async def get_subreddit_posts(
    subreddit: str,
    sort: str = Query("hot", pattern="^(hot|new|top|rising)$"),
    time_filter: Optional[str] = Query(
        None,
        description="Only used for sort=top",
        pattern="^(hour|day|week|month|year|all)$",
    ),
    limit: int = Query(20, ge=1, le=100),
):
    try:
        posts = await fetch_subreddit_posts(
            subreddit=subreddit,
            sort=sort,
            time_filter=time_filter,
            limit=limit,
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve)) from ve
    except Exception as exc:  # pragma: no cover - safety net
        raise HTTPException(status_code=502, detail="Failed to fetch subreddit") from exc

    return PostsResponse(
        subreddit=subreddit,
        sort=sort,
        time_filter=time_filter,
        limit=limit,
        posts=[RedditPost(**p) for p in posts],
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Chat endpoint that uses OpenAI and vector search to answer banking questions.
    """
    try:
        response = chat_with_context(request.message)
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@app.get("/")
def root() -> dict:
    return {
        "name": "Voice of Customer API",
        "endpoints": [
            {"GET": "/health"},
            {"GET": "/reddit/{subreddit}?sort=hot|new|top|rising&time_filter=day&limit=20"},
            {"POST": "/chat - Send a chat message"},
        ],
    }



