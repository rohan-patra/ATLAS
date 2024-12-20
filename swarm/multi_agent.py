from swarm import Swarm, Agent
import os
from dotenv import load_dotenv
import csv
from datetime import datetime
import uuid

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = Swarm()

# current issues:
# the agents are not properly responding to changes when prompting ie if you want to negotiate a higher price for an item as a buyer or vice versa as a seller it does not work
# dialogue is cluttered with recommendations of actions, the dialogue should be clear


def product_verification_agent():
    """Agent responsible for verifying product details and authenticity"""
    return Agent(
        name="Product Verification Agent",
        system_prompt="""Verify this product's details, authenticity, and marketplace standards. 
        Report any concerns or issues immediately.""",
        tools=[],
    )


def price_negotiation_agent():
    """Agent managing the price negotiation process"""
    return Agent(
        name="Price Negotiation Agent",
        system_prompt="""Facilitate price negotiations professionally. Make or evaluate offers based on 
        market value and budget constraints.""",
        tools=[],
    )


def negotiation_abort_agent():
    """Agent handling negotiation termination"""
    return Agent(
        name="Negotiation Abort Agent",
        system_prompt="""Handle negotiation termination professionally and document the reason.""",
        tools=[],
    )


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


def marketplace_negotiation(
    product_details, buyer_budget, seller_min_price, user_role="buyer", interactive=True
):
    """Orchestrates the marketplace interaction between agents"""
    # Create new conversation
    conversation_id = str(uuid.uuid4())
    create_conversation_file(conversation_id)

    print("\n=== Starting Marketplace Negotiation ===")
    print(f"Conversation ID: {conversation_id}")
    print(f"Product: {product_details['name']}")
    print(f"Listed Price: ${product_details['price']}")

    # Display role-specific information
    if user_role == "buyer":
        print(f"Your Budget (as buyer): ${buyer_budget}")
        print(f"[Hidden from buyer agent] Seller Minimum: ${seller_min_price}")
    else:
        print(f"[Hidden from seller agent] Buyer Budget: ${buyer_budget}")
        print(f"Your Minimum Price (as seller): ${seller_min_price}")

    def get_user_instruction(stage):
        if interactive:
            print(
                f"\n💭 Enter instructions for your {user_role} agent (press Enter to skip):"
            )
            return input("> ").strip()
        return ""

    # Step 1: Product Verification
    print("\n--- Step 1: Product Verification ---")
    user_instruction = get_user_instruction("verification")

    verifier = Agent(
        name="Product Verification Agent",
        system_prompt=f"""You are verifying this product for the {user_role}.
        Your ONLY task is to verify if this product meets marketplace standards.
        
        Format your response EXACTLY like this:
        VERIFICATION: [YES/NO]
        REASON: [One brief sentence explaining why]
        
        Do not provide recommendations, steps, or checklists.
        If no specific concerns are provided, assume the product meets standards.""",
        tools=[],
    )

    verification_result = client.run(
        agent=verifier,
        messages=[
            {
                "role": "user",
                "content": f"Verify this product: {product_details}"
                + (f"\nUser concerns: {user_instruction}" if user_instruction else ""),
            }
        ],
    )

    print(f"\n🔍 Verification Result: {verification_result.messages[-1]['content']}")

    if "no" in verification_result.messages[-1]["content"].lower():
        return {
            "status": False,
            "final_price": None,
            "message": "Verification failed - product did not meet marketplace standards",
        }

    # Step 2: Price Negotiation
    print("\n--- Starting Price Negotiation ---")
    current_price = product_details["price"]
    max_rounds = 5
    final_result = {"status": False, "final_price": None, "message": ""}

    # Log initial greetings
    now = datetime.utcnow().isoformat() + "Z"
    log_message(
        conversation_id, {"dateTime": now, "content": "Hello", "sender": "buyer"}
    )
    log_message(
        conversation_id, {"dateTime": now, "content": "Hello", "sender": "seller"}
    )

    for round_num in range(max_rounds):
        print(f"\n=== Round {round_num + 1}/{max_rounds} ===")
        print(f"Current price: ${current_price}")

        # Get user instruction for this round
        user_instruction = get_user_instruction(f"round {round_num + 1}")

        # Buyer's turn
        buyer_agent = Agent(
            name="Buyer Agent",
            system_prompt=f"""You are negotiating as the buyer.
            Budget: ${buyer_budget}
            Current price: ${current_price}
            
            IMPORTANT: Respond in a direct, conversational way. 
            Start with your offer amount and then give a SHORT explanation.
            Format: "I offer $X because [brief reason]"
            
            Consider user instructions: {user_instruction if user_role == 'buyer' else ''}""",
            tools=[],
        )

        buyer_response = client.run(
            agent=buyer_agent,
            messages=[
                {
                    "role": "user",
                    "content": f"Make an offer for the {product_details['name']} currently at ${current_price}.",
                }
            ],
        )

        buyer_message = buyer_response.messages[-1]["content"]
        print(f"\n🛍️  Buyer: {buyer_message}")

        # Extract buyer's offer
        buyer_offer = extract_offer(buyer_response.messages[-1]["content"])
        if buyer_offer:
            # Log the offer
            now = datetime.utcnow().isoformat() + "Z"
            log_message(
                conversation_id,
                {
                    "dateTime": now,
                    "content": "",
                    "sender": "buyer",
                    "type": "offer",
                    "price": buyer_offer,
                },
            )
        else:
            # Log regular message
            now = datetime.utcnow().isoformat() + "Z"
            log_message(
                conversation_id,
                {"dateTime": now, "content": buyer_message, "sender": "buyer"},
            )
            print("❌ Invalid offer - skipping round")
            continue

        # Seller's turn
        seller_agent = Agent(
            name="Seller Agent",
            system_prompt=f"""You are negotiating as the seller.
            Minimum acceptable price: ${seller_min_price}
            Current offer: ${buyer_offer}
            
            IMPORTANT: Respond in a direct, conversational way.
            Use EXACTLY one of these formats:
            - "ACCEPT: [brief acceptance message]"
            - "COUNTER: $X [brief reason]"
            - "REJECT: [brief reason]"
            
            Consider user instructions: {user_instruction if user_role == 'seller' else ''}""",
            tools=[],
        )

        seller_response = client.run(
            agent=seller_agent,
            messages=[
                {
                    "role": "user",
                    "content": f"Respond to buyer's offer of ${buyer_offer}",
                }
            ],
        )

        seller_message = seller_response.messages[-1]["content"]
        print(f"\n💼 Seller: {seller_message}")

        now = datetime.utcnow().isoformat() + "Z"

        # Process seller's response
        response = seller_response.messages[-1]["content"].lower()
        if "accept" in response:
            # Log acceptance
            log_message(
                conversation_id,
                {
                    "dateTime": now,
                    "content": "",
                    "sender": "seller",
                    "type": "accepted",
                    "price": buyer_offer,
                },
            )
            final_result = {
                "status": True,
                "final_price": buyer_offer,
                "message": f"Deal successfully concluded at ${buyer_offer}",
            }
            print(f"\n✅ Deal agreed at ${buyer_offer}!")
            return final_result
        else:
            # Log regular message
            log_message(
                conversation_id,
                {"dateTime": now, "content": seller_message, "sender": "seller"},
            )

            if "reject" in response:
                if round_num == max_rounds - 1:
                    final_result["message"] = (
                        "Negotiation failed - maximum rounds reached"
                    )
                    print("\n❌ Negotiation failed - maximum rounds reached")
                    return final_result
                continue
            else:
                counter_offer = extract_offer(response)
                if counter_offer:
                    current_price = counter_offer
                    print(f"\n💰 New price: ${current_price}")

    final_result["message"] = "Negotiation failed - no agreement reached"
    print("\n❌ Negotiation failed - no agreement reached")
    return final_result


def extract_offer(message):
    """Extract numerical offer from message"""
    import re

    matches = re.findall(r"\$(\d+)", message)
    return int(matches[0]) if matches else None


# Sample usage
if __name__ == "__main__":
    print("\n🏪 Starting Marketplace Demo 🏪")
    product_details = {
        "name": "Victorian Sofa",
        "description": "1960s Vintage British Sofa",
        "condition": "Excellent",
        "price": 1000,
        "category": "Furniture",
    }

    print("\n1. Buyer")
    print("2. Seller")
    role_choice = input("> ").strip()
    user_role = "buyer" if role_choice == "1" else "seller"

    result = marketplace_negotiation(
        product_details=product_details,
        buyer_budget=900,
        seller_min_price=800,
        user_role=user_role,
        interactive=True,
    )

    print("\n=== Final Negotiation Result ===")
    print(result["message"])
    if result["status"]:
        print(f"Final agreed price: ${result['final_price']}")
    print("\n🏁 Marketplace Demo Complete 🏁")
