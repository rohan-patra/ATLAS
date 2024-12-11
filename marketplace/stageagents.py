from swarm import Swarm, Agent
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Initialize Swarm client
client = Swarm()

# Transfer Functions
def transfer_to_product_verification():
    return product_verification_agent

def transfer_to_initial_negotiation():
    return initial_negotiation_agent

def transfer_to_price_negotiation():
    return price_negotiation_agent

def transfer_to_shipping_details():
    return shipping_details_agent

def transfer_to_transaction_closure():
    return transaction_closure_agent

def transfer_to_negotiation_abort():
    return negotiation_abort_agent

# Agents Definition
def product_verification_instructions(context_variables):
    product = context_variables.get('product', {}) if isinstance(context_variables, dict) else {}
    return f"""You are a Product Verification Agent in an online marketplace.
    Verify the authenticity, condition, and details of the following product:
    - Name: {product.get('name', 'N/A')}
    - Description: {product.get('description', 'N/A')}
    - Initial Price: ${product.get('price', 'N/A')}
    
    Your tasks:
    1. Confirm product details are accurate
    2. Check for any potential issues or discrepancies
    3. Determine if the product is ready for negotiation
    4. If verified, transfer to initial negotiation
    5. If issues found, recommend abort or further investigation"""

def product_verification_function(context):
    product = context.get('product', {}) if isinstance(context, dict) else {}
    if not product or not product.get('name') or not product.get('price'):
        return "Product verification failed. Missing or incomplete details."
    return "Product verified. Ready for negotiation."

product_verification_agent = Agent(
    name="Product Verification Agent",
    instructions=product_verification_instructions,
    functions=[
        product_verification_function,
        transfer_to_initial_negotiation,
        transfer_to_negotiation_abort
    ],
)

def initial_negotiation_instructions(context_variables):
    product = context_variables.get('product', {}) if isinstance(context_variables, dict) else {}
    buyer_preferences = context_variables.get('buyer_preferences', {}) if isinstance(context_variables, dict) else {}
    return f"""You are an Initial Negotiation Agent in an online marketplace.
    Product Details:
    - Name: {product.get('name', 'N/A')}
    - Initial Price: ${product.get('price', 'N/A')}
    
    Buyer Preferences:
    - Budget: ${buyer_preferences.get('max_budget', 'N/A')}
    - Desired Discount: {buyer_preferences.get('desired_discount', 'N/A')}
    
    Your tasks:
    1. Assess initial negotiation strategy
    2. Determine opening offer
    3. Prepare for price negotiation"""

def initial_negotiation_function(context):
    product_price = float(context.get('product', {}).get('price', 0)) if isinstance(context, dict) else 0
    max_budget = float(context.get('buyer_preferences', {}).get('max_budget', 0)) if isinstance(context, dict) else 0
    if product_price == 0 or max_budget == 0:
        return "Unable to create initial negotiation strategy. Insufficient information."
    initial_offer = min(product_price * 0.8, max_budget)
    return f"Initial offer: ${initial_offer:.2f}"

initial_negotiation_agent = Agent(
    name="Initial Negotiation Agent",
    instructions=initial_negotiation_instructions,
    functions=[
        initial_negotiation_function,
        transfer_to_price_negotiation,
        transfer_to_negotiation_abort
    ],
)

def price_negotiation_instructions(context_variables):
    product = context_variables.get('product', {}) if isinstance(context_variables, dict) else {}
    previous_offers = context_variables.get('previous_offers', []) if isinstance(context_variables, dict) else []
    return f"""You are a Price Negotiation Agent in an online marketplace.
    Product Details:
    - Name: {product.get('name', 'N/A')}
    - Initial Price: ${product.get('price', 'N/A')}
    
    Negotiation History:
    - Previous Offers: {previous_offers}
    
    Your tasks:
    1. Analyze previous offers
    2. Make strategic counter-offers
    3. Aim to reach a mutually acceptable price
    4. Know when to accept or continue negotiating"""

def price_negotiation_function(context):
    product_price = float(context.get('product', {}).get('price', 0)) if isinstance(context, dict) else 0
    previous_offers = context.get('previous_offers', []) if isinstance(context, dict) else []
    if not previous_offers:
        return "No previous offers to negotiate from."
    last_offer = float(previous_offers[-1])
    if last_offer >= product_price * 0.9:
        return f"Accept offer of ${last_offer:.2f}"
    else:
        counter_offer = (product_price + last_offer) / 2
        return f"Counter-offer: ${counter_offer:.2f}"

price_negotiation_agent = Agent(
    name="Price Negotiation Agent",
    instructions=price_negotiation_instructions,
    functions=[
        price_negotiation_function,
        transfer_to_shipping_details,
        transfer_to_negotiation_abort
    ],
)

def shipping_details_instructions(context_variables):
    product = context_variables.get('product', {}) if isinstance(context_variables, dict) else {}
    agreed_price = context_variables.get('agreed_price', 0) if isinstance(context_variables, dict) else 0
    return f"""You are a Shipping Details Agent in an online marketplace.
    Product Details:
    - Name: {product.get('name', 'N/A')}
    - Agreed Price: ${agreed_price}
    
    Your tasks:
    1. Confirm shipping options
    2. Verify delivery details
    3. Prepare for transaction closure"""

shipping_details_agent = Agent(
    name="Shipping Details Agent",
    instructions=shipping_details_instructions,
    functions=[
        transfer_to_transaction_closure,
        transfer_to_negotiation_abort
    ],
)

def transaction_closure_instructions(context_variables):
    product = context_variables.get('product', {}) if isinstance(context_variables, dict) else {}
    agreed_price = context_variables.get('agreed_price', 0) if isinstance(context_variables, dict) else 0
    return f"""You are a Transaction Closure Agent in an online marketplace.
    Finalize Transaction Details:
    - Product: {product.get('name', 'N/A')}
    - Final Price: ${agreed_price}
    
    Your tasks:
    1. Confirm all transaction details
    2. Prepare payment and shipping instructions
    3. Complete the marketplace transaction"""

def transaction_closure_function(context):
    product = context.get('product', {}) if isinstance(context, dict) else {}
    agreed_price = context.get('agreed_price', 0) if isinstance(context, dict) else 0
    if not product or agreed_price == 0:
        return "Transaction cannot be completed. Insufficient details."
    return f"Transaction completed for {product.get('name')} at ${agreed_price}"

transaction_closure_agent = Agent(
    name="Transaction Closure Agent",
    instructions=transaction_closure_instructions,
    functions=[
        transaction_closure_function
    ],
)

def negotiation_abort_instructions(context_variables):
    abort_reason = context_variables.get('abort_reason', 'Unspecified') if isinstance(context_variables, dict) else 'Unspecified'
    return f"""You are a Negotiation Abort Agent in an online marketplace.
    Negotiation Termination:
    - Reason: {abort_reason}
    
    Your tasks:
    1. Provide clear explanation for negotiation failure
    2. Suggest potential next steps"""

negotiation_abort_agent = Agent(
    name="Negotiation Abort Agent",
    instructions=negotiation_abort_instructions,
    functions=[]
)

# Main Negotiation Function
def marketplace_negotiation():
    # Sample product and buyer information
    negotiation_context = {
        'product': {
            'name': 'Vintage Camera',
            'description': 'Rare vintage film camera in good condition',
            'price': 500.00,
            'condition': 'Good'
        },
        'buyer_preferences': {
            'max_budget': 400.00,
            'desired_discount': 0.2
        },
        'previous_offers': []
    }

    # Start with product verification
    current_agent = product_verification_agent

    # Negotiation simulation
    while current_agent != transaction_closure_agent and current_agent != negotiation_abort_agent:
        # Run the current agent
        response = client.run(
            agent=current_agent,
            messages=[],
            context_variables=negotiation_context
        ).messages[-1]["content"]

        # Debug logs
        print(f"Agent: {current_agent.name}")
        print(f"Response: {response}")

        # Update context and switch agents
        if "verified" in response.lower():
            current_agent = transfer_to_initial_negotiation()
        elif "initial offer" in response.lower():
            negotiation_context['previous_offers'].append(response.split('$')[1])
            current_agent = transfer_to_price_negotiation()
        elif "counter-offer" in response.lower():
            negotiation_context['previous_offers'].append(response.split('$')[1])
        elif "accept offer" in response.lower():
            negotiation_context['agreed_price'] = float(response.split('$')[1])
            current_agent = transfer_to_shipping_details()
        elif "failed" in response.lower():
            current_agent = transfer_to_negotiation_abort()
            negotiation_context['abort_reason'] = "Product verification failed"

    # Final stage
    if current_agent == transaction_closure_agent:
        final_result = client.run(
            agent=current_agent,
            messages=[],
            context_variables=negotiation_context
        ).messages[-1]["content"]
        print(final_result)
    else:
        print(f"Negotiation aborted. Reason: {negotiation_context.get('abort_reason', 'Unspecified')}")

# Run the negotiation
if __name__ == "__main__":
    marketplace_negotiation()
