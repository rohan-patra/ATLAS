from openai import OpenAI
from swarm import Agent, Swarm
import time
import os
from dotenv import load_dotenv
import re

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

client = OpenAI()

# sample item, change whenever
ITEM = {
    "name": "Vintage Mechanical Keyboard",
    "condition": "Used - Like New",
    "original_price": 200,
    "listing_price": 180,
    "description": "IBM Model M mechanical keyboard from 1989. All keys work perfectly. Includes original USB adapter.",
    "minimum_acceptable_price": 150
}

def create_system_prompt(role):
    if role == "seller":
        return """You are a marketplace seller on a casual messaging platform. Use a conversational, text-message style (casual but professional).
                 You're selling a specific item and must engage with the buyer. Be firm on pricing but willing to negotiate.
                 Keep responses brief and natural. Only mention price when making/responding to offers."""
    else:
        return """You are a marketplace buyer on a casual messaging platform. Use a conversational, text-message style.
                 You're interested in the item but want the best possible price. First check the item's condition,
                 then negotiate firmly but reasonably. Keep responses brief and natural, like texting."""

def extract_price(message):
    """Extract price from a message using regex to find dollar amounts."""
    price_matches = re.findall(r'\$(\d+)', message)
    if price_matches:
        return int(price_matches[-1])
    return None

def simulate_negotiation():

    seller_system = create_system_prompt("seller") + "\nYou are responding as the SELLER. The other person is the BUYER."
    buyer_system = create_system_prompt("buyer") + "\nYou are responding as the BUYER. The other person is the SELLER."
    
    # Create initial buyer message
    buyer_first_message = f"Hi! I saw your {ITEM['name']} listed for ${ITEM['listing_price']}. Could you tell me more about its condition?"
    

    conversation_history = []
    

    conversation_history.append({
        "role": "user",
        "content": f"[BUYER]: {buyer_first_message}"
    })
    
    round_count = 0
    deal_made = False
    final_price = None
    
    while round_count < 5 and not deal_made:
        print(f"\n--- Round {round_count + 1} ---")
        
        # Seller's turn
        seller_messages = [
            {"role": "system", "content": seller_system},
            *conversation_history
        ]
        
        seller_response = client.chat.completions.create(
            model="gpt-4",
            messages=seller_messages,
            temperature=0.7,
            max_tokens=150 
        )
        seller_message = seller_response.choices[0].message.content
        conversation_history.append({
            "role": "assistant",
            "content": f"[SELLER]: {seller_message}"
        })
        print(f"💬 Seller: {seller_message}")
        

        if "deal" in seller_message.lower() or "sold" in seller_message.lower():
            deal_made = True
            final_price = extract_price(seller_message)
            if not final_price:
                final_price = ITEM['listing_price']
            break
            
        # Buyer's turn
        buyer_messages = [
            {"role": "system", "content": buyer_system},
            *conversation_history
        ]
        
        buyer_response = client.chat.completions.create(
            model="gpt-4",
            messages=buyer_messages,
            temperature=0.7,
            max_tokens=150 
        )
        buyer_message = buyer_response.choices[0].message.content
        conversation_history.append({
            "role": "user",
            "content": f"[BUYER]: {buyer_message}"
        })
        print(f"🛍️ Buyer: {buyer_message}")
        
        # Check if deal is made
        if "deal" in buyer_message.lower() or "sold" in buyer_message.lower():
            deal_made = True
            final_price = extract_price(buyer_message)
            if not final_price: 
                final_price = ITEM['listing_price']
            break
        
        round_count += 1
        time.sleep(1)
    
    if deal_made:
        print(f"\nDeal made at ${final_price}!")
    else:
        print("\nNegotiation ended without a deal.")

if __name__ == "__main__":
    print(f"Starting negotiation for {ITEM['name']}")
    print(f"Listed price: ${ITEM['listing_price']}")
    print("-" * 50)
    simulate_negotiation()
