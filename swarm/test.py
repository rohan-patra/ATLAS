from swarm import Swarm, Agent
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

client = Swarm()

item = {
    "name": "Vintage Watch",
    "description": "A rare, antique watch in excellent condition.",
    "price": 500
}

client = Swarm()

buyer_agent = Agent(
    name="Buyer Agent",
    instructions="You are a buyer trying to purchase an item. Your goal is to minimize the price of the item using negotiation tactics."
)

seller_agent = Agent(
    name="Seller Agent",
    instructions="You are a seller trying to sell an item. Your goal is to maximize the price and resist significant price reductions."
)

def simulate_negotiation(item, max_rounds=5):
    print(f"Item for sale: {item['name']}\nDescription: {item['description']}\nStarting Price: ${item['price']}")

    current_price = item['price']
    messages = []

    for round_number in range(max_rounds):
        print(f"\nRound {round_number + 1}:")

        buyer_message = f"The current price is ${current_price}. I want to offer a lower price."
        messages.append({"role": "user", "content": buyer_message})
        buyer_response = client.run(agent=buyer_agent, messages=messages)
        buyer_offer = buyer_response.messages[-1]["content"]
        print(f"Buyer: {buyer_offer}")

        seller_message = f"The buyer has offered {buyer_offer}. I want to respond to this offer."
        messages.append({"role": "user", "content": seller_message})
        seller_response = client.run(agent=seller_agent, messages=messages)
        seller_counter = seller_response.messages[-1]["content"]
        print(f"Seller: {seller_counter}")

        try:
            current_price = int(seller_counter.strip().split('$')[-1])
        except ValueError:
            print("Invalid price format. Negotiation ends.")
            break

        if "deal" in seller_counter.lower():
            print(f"\nDeal reached at ${current_price}!")
            return

    print("\nNo deal was made. Buyer and seller could not agree on a price.")

simulate_negotiation(item)