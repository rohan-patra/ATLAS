from swarm import Swarm, Agent
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

client = Swarm()

def product_verification_agent():
    """Agent responsible for verifying product details and authenticity"""
    return Agent(
        name="Product Verification Agent",
        system_prompt="""You are a product verification agent. Your role is to:
        1. Verify product details (name, description, condition)
        2. Check if the product meets marketplace standards
        3. Validate product authenticity
        4. Request additional information if needed
        
        Respond with clear verification status and any concerns.""",
        tools=[] 
    )

def initial_negotiation_agent():
    """Agent handling the initial phase of negotiation"""
    return Agent(
        name="Initial Negotiation Agent",
        system_prompt="""You are an initial negotiation agent. Your role is to:
        1. Establish initial contact between buyer and seller
        2. Gather basic requirements and preferences
        3. Confirm listing price and buyer's interest
        4. Set the stage for price negotiation
        
        Keep the conversation professional and focused on moving to price discussion.""",
        tools=[]
    )

def price_negotiation_agent():
    """Agent managing the price negotiation process"""
    return Agent(
        name="Price Negotiation Agent",
        system_prompt="""You are a price negotiation agent. Your role is to:
        1. Facilitate price negotiations between buyer and seller
        2. Evaluate offers and counteroffers
        3. Consider market conditions and item value
        4. Work towards a mutually acceptable price
        5. Know when to transfer to transaction closure or abort
        
        Maintain fairness and professionalism throughout the negotiation.""",
        tools=[]
    )

def shipping_details_agent():
    """Agent handling shipping logistics"""
    return Agent(
        name="Shipping Details Agent",
        system_prompt="""You are a shipping details agent. Your role is to:
        1. Collect shipping information from buyer
        2. Calculate shipping costs
        3. Explain shipping options and timeframes
        4. Handle special shipping requirements
        5. Verify addresses and delivery preferences
        
        Ensure all shipping details are clear and accurate.""",
        tools=[]
    )

def transaction_closure_agent():
    """Agent managing the final transaction process"""
    return Agent(
        name="Transaction Closure Agent",
        system_prompt="""You are a transaction closure agent. Your role is to:
        1. Summarize the agreed terms
        2. Confirm final price including shipping
        3. Guide through payment process
        4. Provide transaction documentation
        5. Ensure both parties understand next steps
        
        Make sure all aspects of the deal are clear and documented.""",
        tools=[]
    )

def negotiation_abort_agent():
    """Agent handling negotiation termination"""
    return Agent(
        name="Negotiation Abort Agent",
        system_prompt="""You are a negotiation abort agent. Your role is to:
        1. Handle graceful termination of negotiations
        2. Document reason for termination
        3. Provide alternative suggestions if applicable
        4. Maintain professional relationship for future interactions
        5. Collect feedback for system improvement
        
        Keep the interaction professional even when dealing with unsuccessful negotiations.""",
        tools=[]
    )

def marketplace_negotiation(product_details, buyer_budget, seller_min_price, user_role='buyer', interactive=True):
    """
    Orchestrates the complete marketplace interaction between agents
    
    Args:
        product_details (dict): Details of the product being sold
        buyer_budget (float): Maximum budget for the buyer
        seller_min_price (float): Minimum acceptable price for the seller
        user_role (str): Role of the user ('buyer' or 'seller')
        interactive (bool): Whether to allow user instructions during negotiation
    """
    print("\n=== Starting Marketplace Negotiation ===")
    print(f"Product: {product_details['name']}")
    print(f"Listed Price: ${product_details['price']}")
    
    # Display information based on user role
    if user_role == 'buyer':
        print(f"Your Budget (as buyer): ${buyer_budget}")
        print(f"[Hidden from you] Seller Minimum: ${seller_min_price}")
    else:  # seller
        print(f"[Hidden from you] Buyer Budget: ${buyer_budget}")
        print(f"Your Minimum Price (as seller): ${seller_min_price}")

    def get_user_instruction(stage):
        if interactive:
            print(f"\n[Optional] As the {user_role}, enter your instructions for {stage}")
            print(f"These instructions will guide your {user_role} agent's behavior.")
            print("Press Enter to skip, or type your instructions:")
            return input(f"{user_role.title()}'s Instructions > ").strip()
        return ""

    # Initialize abort agent
    abort = negotiation_abort_agent()

    # Step 1: Product Verification
    print(f"\n--- Step 1: Product Verification ---")
    user_instruction = get_user_instruction("Product Verification")
    base_context = f"\n{user_role.title()}'s Instructions: {user_instruction}" if user_instruction else ""
    
    verifier = Agent(
        name=f"Product Verification Agent ({user_role.title()}'s Agent)",
        system_prompt=f"""You are a product verification agent working for the {user_role}. Your role is to:
        1. Verify product details (name, description, condition)
        2. Check if the product meets marketplace standards
        3. Validate product authenticity
        4. Request additional information if needed
        
        Respond with clear verification status and any concerns.{base_context}""",
        tools=[]
    )

    verification_result = client.run(
        agent=verifier,
        messages=[{
            "role": "user",
            "content": f"Please verify the following product: {product_details}"
        }]
    )
    print("Verification Response:", verification_result.messages[-1]["content"])
    
    if "concerns" in verification_result.messages[-1]["content"].lower():
        print("\n❌ Product verification failed. Aborting...")
        return client.run(
            agent=abort,
            messages=[{
                "role": "user",
                "content": "Product verification failed. Terminate the negotiation."
            }]
        )

    # Step 2: Initial Negotiation
    print("\n--- Step 2: Initial Negotiation ---")
    user_instruction = get_user_instruction("Initial Negotiation")
    base_context = f"\n{user_role.title()}'s Instructions: {user_instruction}" if user_instruction else ""
    
    initial_neg = Agent(
        name="Initial Negotiation Agent",
        system_prompt=f"""You are an initial negotiation agent. Your role is to:
        1. Establish initial contact between buyer and seller
        2. Gather basic requirements and preferences
        3. Confirm listing price and buyer's interest
        4. Set the stage for price negotiation
        
        Keep the conversation professional and focused on moving to price discussion.{base_context}""",
        tools=[]
    )

    initial_result = client.run(
        agent=initial_neg,
        messages=[{
            "role": "user",
            "content": f"""
            Product details: {product_details}
            Listing price: ${product_details.get('price')}
            Buyer budget: ${buyer_budget}
            """
        }]
    )
    print("Initial Negotiation Response:", initial_result.messages[-1]["content"])

    if "not interested" in initial_result.messages[-1]["content"].lower():
        print("\n❌ Buyer not interested. Aborting...")
        return client.run(
            agent=abort,
            messages=[{
                "role": "user",
                "content": "Buyer not interested. Terminate the negotiation."
            }]
        )

    # Step 3: Price Negotiation
    print("\n--- Step 3: Price Negotiation ---")
    max_rounds = 5
    current_offer = None
    
    for round_num in range(max_rounds):
        print(f"\nRound {round_num + 1}/{max_rounds}")
        user_instruction = get_user_instruction(f"Price Negotiation Round {round_num + 1}")
        base_context = f"\n{user_role.title()}'s Instructions: {user_instruction}" if user_instruction else ""
        
        price_neg = Agent(
            name="Price Negotiation Agent",
            system_prompt=f"""You are a price negotiation agent. Your role is to:
            1. Facilitate price negotiations between buyer and seller
            2. Evaluate offers and counteroffers
            3. Consider market conditions and item value
            4. Work towards a mutually acceptable price
            5. Know when to transfer to transaction closure or abort
            
            Maintain fairness and professionalism throughout the negotiation.{base_context}""",
            tools=[]
        )

        price_result = client.run(
            agent=price_neg,
            messages=[{
                "role": "user",
                "content": f"""
                Round {round_num + 1}
                Current offer: ${current_offer if current_offer else 'None'}
                Listing price: ${product_details.get('price')}
                Buyer budget: ${buyer_budget}
                Seller minimum: ${seller_min_price}
                """
            }]
        )
        
        response = price_result.messages[-1]["content"]
        print("Negotiation Response:", response)
        
        if "agreement reached" in response.lower():
            print("\n✅ Agreement reached!")
            break
        elif "terminate" in response.lower():
            print("\n❌ Price negotiation failed. Aborting...")
            return client.run(
                agent=abort,
                messages=[{
                    "role": "user",
                    "content": "Price negotiation failed. Terminate the negotiation."
                }]
            )
        
        current_offer = extract_offer(response)
        print(f"Extracted offer: ${current_offer}")

    # Step 4: Shipping Details
    if "agreement reached" in response.lower():
        print("\n--- Step 4: Shipping Details ---")
        user_instruction = get_user_instruction("Shipping Details")
        base_context = f"\n{user_role.title()}'s Instructions: {user_instruction}" if user_instruction else ""
        
        shipping = Agent(
            name="Shipping Details Agent",
            system_prompt=f"""You are a shipping details agent. Your role is to:
            1. Collect shipping information from buyer
            2. Calculate shipping costs
            3. Explain shipping options and timeframes
            4. Handle special shipping requirements
            5. Verify addresses and delivery preferences
            
            Ensure all shipping details are clear and accurate.{base_context}""",
            tools=[]
        )

        shipping_result = client.run(
            agent=shipping,
            messages=[{
                "role": "user",
                "content": f"""
                Agreement reached at ${current_offer}
                Please handle shipping details for:
                Product: {product_details}
                """
            }]
        )
        print("Shipping Response:", shipping_result.messages[-1]["content"])

        # Step 5: Transaction Closure
        print("\n--- Step 5: Transaction Closure ---")
        user_instruction = get_user_instruction("Transaction Closure")
        base_context = f"\n{user_role.title()}'s Instructions: {user_instruction}" if user_instruction else ""
        
        closure = Agent(
            name="Transaction Closure Agent",
            system_prompt=f"""You are a transaction closure agent. Your role is to:
            1. Summarize the agreed terms
            2. Confirm final price including shipping
            3. Guide through payment process
            4. Provide transaction documentation
            5. Ensure both parties understand next steps
            
            Make sure all aspects of the deal are clear and documented.{base_context}""",
            tools=[]
        )

        final_result = client.run(
            agent=closure,
            messages=[{
                "role": "user",
                "content": f"""
                Final price: ${current_offer}
                Shipping details: {shipping_result.messages[-1]["content"]}
                Please finalize the transaction.
                """
            }]
        )
        print("\n✅ Transaction completed!")
        return final_result
    
    print("\n❌ Maximum rounds reached without agreement. Aborting...")
    return client.run(
        agent=abort,
        messages=[{
            "role": "user",
            "content": "Maximum rounds reached without agreement. Terminate the negotiation."
        }]
    )

def extract_offer(response):
    """Helper function to extract numerical offer from agent response"""
    # Implementation needed: Extract dollar amount from response
    # place holder -- we can add api interaction here with fb marketplace or any other online marketplace
    import re
    matches = re.findall(r'\$(\d+)', response)
    return int(matches[0]) if matches else None

# Sample usage
if __name__ == "__main__":
    print("\n🏪 Starting Marketplace Demo 🏪")
    product_details = {
        "name": "Victorian Sofa",
        "description": "1960s Vintage British Sofa",
        "condition": "Excellent",
        "price": 1000,
        "category": "Furniture"
    }
    
    # Let user choose their role
    print("\nChoose your role in the marketplace:")
    print("1. Buyer")
    print("2. Seller")
    role_choice = input("Enter 1 or 2: ").strip()
    user_role = 'buyer' if role_choice == '1' else 'seller'
    
    print(f"\nYou are the {user_role.upper()} in this marketplace negotiation.")
    print(f"You will be prompted to give instructions to your {user_role} agent at each stage.")
    print(f"Your agent will negotiate on your behalf based on your instructions.")
    print("(Press Enter to skip giving instructions for any stage)")
    
    result = marketplace_negotiation(
        product_details=product_details,
        buyer_budget=900,
        seller_min_price=800,
        user_role=user_role,
        interactive=True
    )
    
    print("\n=== Final Negotiation Result ===")
    print(result.messages[-1]["content"])
    print("\n🏁 Marketplace Demo Complete 🏁")

