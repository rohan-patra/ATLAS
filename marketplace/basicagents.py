from swarm import Swarm, Agent
import os
from dotenv import load_dotenv # type: ignore

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

client = Swarm()

# Define the Buyer Agent
def make_offer(listing_price, max_price, previous_offer):
    # Convert all inputs to integers
    listing_price = int(listing_price)
    max_price = int(max_price)
    previous_offer = int(previous_offer) if previous_offer else 0

    # Calculate the new offer
    new_offer = min(max_price, previous_offer + 10) if previous_offer else min(max_price, listing_price - 20)

    # Debug output to check values
    print(f"Previous Offer: {previous_offer}, Listing Price: {listing_price}, Max Price: {max_price}")
    print(f"New Offer: {new_offer}")

    return f"My offer is ${new_offer}."

buyer_agent = Agent(
    name="Buyer Agent",
    instructions=(
        "You are a buyer agent. Negotiate to get the item for the lowest price possible. "
        "Consider the listing price and your budget. Make incremental offers if rejected."
    ),
    functions=[make_offer],
)

# Define the Seller Agent
def respond_to_offer(buyer_offer, listing_price, min_price, urgency):
    # Convert all inputs to integers
    buyer_offer = int(buyer_offer)
    listing_price = int(listing_price)
    min_price = int(min_price)

    if buyer_offer >= min_price:
        return f"Accept offer of ${buyer_offer}."
    counter_offer = max(min_price, buyer_offer + 10)
    return f"Counteroffer: ${counter_offer}. I cannot go lower."

seller_agent = Agent(
    name="Seller Agent",
    instructions=(
        "You are a seller agent. Negotiate to get the best possible price for the item. "
        "Never go below the minimum price and prioritize urgency if the buyer seems motivated."
    ),
    functions=[respond_to_offer],
)

# Simulate Negotiation
def negotiate():
    # Initialize listing details
    listing_price = 100
    min_price = 80
    max_price = 90
    urgency = "medium"
    previous_offer = None

    print("Negotiation begins!")
    for round_num in range(5):  # Maximum of 5 negotiation rounds
        print(f"--- Round {round_num + 1} ---")

        # Buyer makes an offer
        buyer_response = client.run(
            agent=buyer_agent,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Listing price: ${listing_price}. "
                        f"Make an offer considering max budget ${max_price}."
                    ),
                }
            ],
            context_variables={
                "listing_price": int(listing_price), 
                "max_price": int(max_price), 
                "previous_offer": int(previous_offer) if previous_offer else 0,
            },
        )
        buyer_offer = int(buyer_response.messages[-1]["content"].split("$")[-1])
        print(f"Buyer: {buyer_response.messages[-1]['content']}")

        # Seller responds
        seller_response = client.run(
            agent=seller_agent,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Buyer offers ${buyer_offer}. "
                        f"Respond considering listing price ${listing_price} and minimum price ${min_price}."
                    ),
                }
            ],
            context_variables={
                "buyer_offer": buyer_offer,
                "listing_price": int(listing_price), 
                "min_price": int(min_price), 
                "urgency": urgency,
            },
        )
        seller_reply = seller_response.messages[-1]["content"]
        print(f"Seller: {seller_reply}")

        # Check for deal acceptance
        if "Accept" in seller_reply:
            print("Deal reached!")
            break

        # Update for the next round
        previous_offer = buyer_offer

    print("Negotiation ended!")

# Run the negotiation
negotiate()
