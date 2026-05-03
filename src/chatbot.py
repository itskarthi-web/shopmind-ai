import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import os
from groq import Groq
from dotenv import load_dotenv
try:
    from src.retriever import search_products, format_products_for_ai
except ImportError:
    from retriever import search_products, format_products_for_ai
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are ShopMind AI, a friendly and intelligent shopping assistant for an Amazon-like store.

Your job:
1. Understand what the customer wants to buy
2. You will be given a list of REAL products from our database
3. Recommend the BEST 2-3 products from that list
4. Explain WHY each product suits their needs
5. Mention price, rating, and any discount
6. Always be friendly, concise, and helpful
7. If the customer asks a follow-up, remember the conversation context

Rules:
- Only recommend products from the list given to you
- Always mention the price clearly with ₹ symbol
- If no products match well, say so honestly
- Keep responses under 200 words
- End with a helpful follow-up question"""


def chat(user_message: str, 
         conversation_history: list) -> tuple[str, list]:
    """
    Main chat function.
    Returns (ai_response, updated_history)
    """

    # STEP 1: Search for relevant products
    products         = search_products(user_message, n_results=5)
    products_context = format_products_for_ai(products)

    # STEP 2: Build the message with product context
    message_with_context = f"""Customer query: {user_message}

Here are relevant products from our database:
{products_context}

Please recommend the best options based on the customer's needs."""

    # STEP 3: Add to conversation history
    conversation_history.append({
        "role"   : "user",
        "content": message_with_context
    })

    # STEP 4: Get AI response
    response = client.chat.completions.create(
        model    = "llama-3.3-70b-versatile",
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ] + conversation_history,
        max_tokens  = 500,
        temperature = 0.7
    )

    ai_response = response.choices[0].message.content

    # STEP 5: Add AI response to history
    conversation_history.append({
        "role"   : "assistant",
        "content": ai_response
    })

    return ai_response, conversation_history, products


def run_terminal_chat():
    """Run chatbot in terminal for testing."""
    print("=" * 60)
    print("🛒 ShopMind AI — Terminal Test Mode")
    print("Type 'quit' to exit")
    print("=" * 60)

    history = []

    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Thanks for shopping! Bye! 👋")
            break
        
        if not user_input:
            continue

        print("\n🤖 ShopMind AI is thinking...")
        
        response, history, products = chat(user_input, history)
        
        print(f"\n🛒 ShopMind: {response}")
        print(f"\n[Found {len(products)} relevant products in database]")


if __name__ == "__main__":
    run_terminal_chat()