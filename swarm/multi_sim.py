from openai import OpenAI
from swarm import Agent, Swarm
import time
import os
from dotenv import load_dotenv
import re
import csv
from datetime import datetime
import uuid

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI()

# sample item, change whenever
ITEM = {
    "name": "Vintage Mechanical Keyboard",
    "condition": "Used - Like New",
    "original_price": 200,
    "listing_price": 180,
    "description": "IBM Model M mechanical keyboard from 1989. All keys work perfectly. Includes original USB adapter.",
    "minimum_acceptable_price": 150,
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
    price_matches = re.findall(r"\$(\d+)", message)
    if price_matches:
        return int(price_matches[-1])
    return None


def get_user_role():
    while True:
        role = input(
            "Would you like to be the buyer or seller? (buyer/seller): "
        ).lower()
        if role in ["buyer", "seller"]:
            return role
        print("Please enter either 'buyer' or 'seller'")


def get_user_message(role, round_num, conversation_history):
    print(f"\n--- Your turn (Round {round_num}) ---")
    print("(Press Enter to skip and let the AI handle this turn)")

    if round_num == 1 and role == "buyer":
        default_message = f"Hi! I saw your {ITEM['name']} listed for ${ITEM['listing_price']}. Could you tell me more about its condition?"
        user_input = input(f"Enter your message as the {role}: ")
        return user_input if user_input.strip() else default_message

    user_input = input(f"Enter your message as the {role}: ")

    if not user_input.strip():
        system_prompt = create_system_prompt(role)
        messages = [{"role": "system", "content": system_prompt}, *conversation_history]
        response = client.chat.completions.create(
            model="gpt-4", messages=messages, temperature=0.7, max_tokens=150
        )
        return response.choices[0].message.content

    return user_input


def create_conversation_file(conversation_id):
    """Create a new conversation CSV file"""
    filepath = f"../marketplace/src/data/conversations/{conversation_id}.csv"
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["dateTime", "content", "sender", "type", "price"])


def log_message(conversation_id, message):
    """Log a message to the conversation CSV file"""
    filepath = f"../marketplace/src/data/conversations/{conversation_id}.csv"
    with open(filepath, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                message["dateTime"],
                message["content"],
                message["sender"],
                message.get("type", "text"),
                message.get("price", ""),
            ]
        )


def verify_product(item, user_role, user_instruction=""):
    """Verify product details and authenticity"""
    verifier = Agent(
        name="Product Verification Agent",
        instructions=f"""You are verifying this product for the {user_role}.
        Your ONLY task is to verify if this product meets marketplace standards.
        
        Format your response EXACTLY like this:
        VERIFICATION: [YES/NO]
        REASON: [One brief sentence explaining why]
        
        Do not provide recommendations, steps, or checklists.
        If no specific concerns are provided, assume the product meets standards.""",
        tools=[],
    )

    verification_result = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": verifier.instructions},
            {
                "role": "user",
                "content": f"Verify this product: {item}"
                + (f"\nUser concerns: {user_instruction}" if user_instruction else ""),
            },
        ],
        temperature=0.7,
        max_tokens=150,
    )

    return verification_result.choices[0].message.content


def simulate_negotiation():
    # Create new conversation at start
    conversation_id = str(uuid.uuid4())
    create_conversation_file(conversation_id)
    print(f"\nConversation ID: {conversation_id}")

    user_role = get_user_role()
    print(f"\nYou are the {user_role}. Let's start the negotiation!")

    # Step 1: Product Verification
    print("\n--- Step 1: Product Verification ---")
    print("Enter any concerns about the product (press Enter to skip):")
    user_instruction = input("> ").strip()

    verification_result = verify_product(ITEM, user_role, user_instruction)
    print(f"\n🔍 Verification Result: {verification_result}")

    if "no" in verification_result.lower():
        print("\n❌ Verification failed - product did not meet marketplace standards")
        return

    # Log initial greeting messages
    now = datetime.utcnow().isoformat() + "Z"
    log_message(
        conversation_id, {"dateTime": now, "content": "Hello", "sender": "buyer"}
    )
    log_message(
        conversation_id, {"dateTime": now, "content": "Hello", "sender": "seller"}
    )

    print("\n--- Starting Price Negotiation ---")

    seller_system = (
        create_system_prompt("seller")
        + "\nYou are responding as the SELLER. The other person is the BUYER."
    )
    buyer_system = (
        create_system_prompt("buyer")
        + "\nYou are responding as the BUYER. The other person is the SELLER."
    )

    conversation_history = []
    round_count = 0
    deal_made = False
    final_price = None

    # Handle initial buyer message
    if user_role == 'buyer':
        buyer_message = get_user_message('buyer', 1, conversation_history)
        print(f"🛍️ Buyer: {buyer_message}")
    else:
        buyer_messages = [
            {"role": "system", "content": buyer_system},
            {"role": "user", "content": f"You're interested in a {ITEM['name']} listed for ${ITEM['listing_price']}. Start the conversation by asking about its condition."}
        ]
        buyer_response = client.chat.completions.create(
            model="gpt-4",
            messages=buyer_messages,
            temperature=0.7,
            max_tokens=150
        )
        buyer_message = buyer_response.choices[0].message.content
        print(f"🛍️ Buyer: {buyer_message}")
    
    conversation_history.append({
        "role": "user",
        "content": f"[BUYER]: {buyer_message}"
    })
    
    while round_count < 5 and not deal_made:
        print(f"\n--- Round {round_count + 1} ---")

        # Seller's turn
        if user_role == "seller":
            seller_message = get_user_message(
                "seller", round_count + 1, conversation_history
            )
        else:
            seller_messages = [
                {"role": "system", "content": seller_system},
                *conversation_history,
            ]
            seller_response = client.chat.completions.create(
                model="gpt-4", messages=seller_messages, temperature=0.7, max_tokens=150
            )
            seller_message = seller_response.choices[0].message.content

        # Log seller's message
        now = datetime.utcnow().isoformat() + "Z"
        price = extract_price(seller_message)
        message_type = "text"
        if "deal" in seller_message.lower() or "sold" in seller_message.lower():
            message_type = "accepted"
        elif price:
            message_type = "offer"

        log_message(
            conversation_id,
            {
                "dateTime": now,
                "content": seller_message,
                "sender": "seller",
                "type": message_type,
                "price": price if price else "",
            },
        )

        if "deal" in seller_message.lower() or "sold" in seller_message.lower():
            deal_made = True
            final_price = extract_price(seller_message)
            if not final_price:
                final_price = ITEM["listing_price"]
            break

        # Buyer's turn
        if user_role == "buyer":
            buyer_message = get_user_message(
                "buyer", round_count + 1, conversation_history
            )
        else:
            buyer_messages = [
                {"role": "system", "content": buyer_system},
                *conversation_history,
            ]
            buyer_response = client.chat.completions.create(
                model="gpt-4", messages=buyer_messages, temperature=0.7, max_tokens=150
            )
            buyer_message = buyer_response.choices[0].message.content

        # Log buyer's message
        now = datetime.utcnow().isoformat() + "Z"
        price = extract_price(buyer_message)
        message_type = "text"
        if "deal" in buyer_message.lower() or "sold" in buyer_message.lower():
            message_type = "accepted"
        elif price:
            message_type = "offer"

        log_message(
            conversation_id,
            {
                "dateTime": now,
                "content": buyer_message,
                "sender": "buyer",
                "type": message_type,
                "price": price if price else "",
            },
        )

        if "deal" in buyer_message.lower() or "sold" in buyer_message.lower():
            deal_made = True
            final_price = extract_price(buyer_message)
            if not final_price:
                final_price = ITEM["listing_price"]
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
