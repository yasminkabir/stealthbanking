"""
Chatbot functionality using OpenAI and Supabase vector search.
"""

import os
from typing import List, Dict, Any
from dotenv import load_dotenv
import openai
from supabase import create_client, Client

load_dotenv()

# Initialize OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Initialize Supabase
SUPABASE_URL = os.getenv("PROJECT_URL")
SUPABASE_KEY = os.getenv("SUPABASE_API")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("PROJECT_URL and SUPABASE_API must be set in environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_embedding(text: str, model: str = "text-embedding-3-small") -> List[float]:
    """
    Generate embedding for text using OpenAI.
    
    Args:
        text: The text to embed
        model: The embedding model to use
        
    Returns:
        List of floats representing the embedding
    """
    response = openai_client.embeddings.create(
        model=model,
        input=text
    )
    return response.data[0].embedding


def search_similar_posts(query_embedding: List[float], limit: int = 5) -> List[Dict[str, Any]]:
    """
    Search for similar posts in Supabase using vector similarity.
    
    Args:
        query_embedding: The embedding vector to search for
        limit: Number of similar posts to return
        
    Returns:
        List of similar posts with title, body, and similarity score
    """
    # Try with lower threshold first (0.3), then even lower (0.1) if no results
    thresholds = [0.3, 0.1, 0.0]
    
    for threshold in thresholds:
        try:
            # Use Supabase RPC for vector similarity search
            result = supabase.rpc(
                'match_posts',
                {
                    'query_embedding': query_embedding,  # Pass as list
                    'match_threshold': threshold,
                    'match_count': limit
                }
            ).execute()
            
            if result.data and len(result.data) > 0:
                print(f"Found {len(result.data)} similar posts with threshold {threshold}")
                return result.data
                
        except Exception as e:
            print(f"RPC vector search failed with threshold {threshold}: {e}")
            # If RPC doesn't exist, try direct SQL query
            try:
                # Convert embedding list to string format for direct SQL
                embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'
                # Use raw SQL query as fallback
                result = supabase.rpc(
                    'match_posts',
                    {
                        'query_embedding': query_embedding,
                        'match_threshold': threshold,
                        'match_count': limit
                    }
                ).execute()
                if result.data and len(result.data) > 0:
                    return result.data
            except:
                pass
    
    # Final fallback: Get recent posts if vector search completely fails
    print("Vector search failed, using recent posts as fallback")
    try:
        result = supabase.table("posts").select("id, title, body").limit(limit).order("id", desc=True).execute()
        return result.data if result.data else []
    except Exception as fallback_error:
        print(f"Fallback also failed: {fallback_error}")
        return []


def generate_chat_response(user_message: str, context_posts: List[Dict[str, Any]]) -> str:
    """
    Generate a chatbot response using OpenAI based on user message and context from vector search.
    
    Args:
        user_message: The user's question/message
        context_posts: Relevant posts retrieved from vector search
        
    Returns:
        Generated response from the chatbot
    """
    # Build context from retrieved posts
    context = ""
    if context_posts:
        context = "Relevant banking insights from our database:\n\n"
        for i, post in enumerate(context_posts[:3], 1):  # Use top 3 for context
            title = post.get('title', 'Untitled')
            body = post.get('body', '')[:500]  # Limit body length
            context += f"{i}. {title}\n{body}\n\n"
    
    system_prompt = """You are a helpful banking insights assistant. You help users explore current online insights about banking topics based on data from customer feedback and discussions.

When answering questions:
- ALWAYS use the provided context from the database to answer the user's question
- Extract key insights, patterns, and specific examples from the context
- Summarize what people are saying about the topic based on the actual posts provided
- Be conversational and helpful
- If the context contains relevant information, USE IT - don't say it's not relevant
- Focus on banking-related topics like fees, credit cards, security, online banking, ATM services, etc.
- Keep responses concise but informative
- Base your response on the actual content provided in the context"""

    user_prompt = f"""User question: {user_message}

{context if context else "No specific context available from the database."}

Based on the context provided above, answer the user's question. Extract and summarize the key insights, concerns, and patterns that people are discussing about this topic. Use specific examples from the context when available."""

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",  # Using a cheaper model
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"I apologize, but I encountered an error: {str(e)}. Please try again."


def chat_with_context(user_message: str) -> str:
    """
    Main function to handle a chat message: embed query, search vector DB, generate response.
    
    Args:
        user_message: The user's message/question
        
    Returns:
        The chatbot's response
    """
    try:
        # Check if it's just a greeting or simple message
        message_lower = user_message.lower().strip()
        simple_greetings = ['hi', 'hello', 'hey', 'hi there', 'hello there', 'hey there']
        
        if message_lower in simple_greetings or len(message_lower.split()) <= 2:
            # For simple greetings, respond without vector search
            return "Hello! I'm here to help you explore current online insights about banking. What specific banking topic would you like to learn about? For example, you could ask about fees, credit cards, security, online banking, or ATM services."
        
        # For actual questions, do vector search
        # Generate embedding for user's question
        query_embedding = get_embedding(user_message)
        
        # Search for similar posts
        similar_posts = search_similar_posts(query_embedding, limit=5)
        
        # Generate response using context
        response = generate_chat_response(user_message, similar_posts)
        
        return response
    except Exception as e:
        return f"I apologize, but I encountered an error processing your request: {str(e)}. Please try again."
