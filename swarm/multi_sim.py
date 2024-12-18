from openai import OpenAI
from swarm import Agent, Swarm
import time
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

client = OpenAI()

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
        return """You are a marketplace seller. You are selling a specific item and must engage with the buyer.
                 Be professional but firm on pricing. You can accept offers but try to maximize your profit.
                 Respond in a natural conversational way. Only state the price when making or responding to offers."""
    else:
        return """You are a marketplace buyer. You're interested in the item but want the best possible price.
                 First verify the item's condition and authenticity, then negotiate firmly but reasonably.
                 Use various negotiation tactics but remain professional. Respond conversationally."""

def simulate_negotiation():
    messages = []
    
    # listing
    seller_system = create_system_prompt("seller")
    buyer_system = create_system_prompt("buyer")
    
    buyer_first_message = f"Hi, I'm interested in your {ITEM['name']} listed for ${ITEM['listing_price']}. Can you tell me more about its condition and authenticity?"
    
    messages.append({"role": "system", "content": seller_system})
    messages.append({"role": "user", "content": buyer_first_message})
    
    round_count = 0
    deal_made = False
    final_price = None
    
    while round_count < 5 and not deal_made:

        seller_response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": seller_system},
                *messages
            ],
            temperature=0.7
        )
        seller_message = seller_response.choices[0].message.content
        messages.append({"role": "assistant", "content": seller_message})
        print(f"\nSeller: {seller_message}")
        

        if "deal" in seller_message.lower() or "sold" in seller_message.lower():
            deal_made = True

            try:
                final_price = int(''.join(filter(str.isdigit, seller_message)))
            except:
                final_price = ITEM['listing_price']
            break
            
        # Buyer's turn
        buyer_response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": buyer_system},
                *messages
            ],
            temperature=0.7
        )
        buyer_message = buyer_response.choices[0].message.content
        messages.append({"role": "user", "content": buyer_message})
        print(f"\nBuyer: {buyer_message}")
        
        # Check if deal is made
        if "deal" in buyer_message.lower() or "sold" in buyer_message.lower():
            deal_made = True
            try:
                final_price = int(''.join(filter(str.isdigit, buyer_message)))
            except:
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
