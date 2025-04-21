import json
import ollama  # Import ollama properly

def generate_api_calls(case: str, sop_file: str) -> dict:
    """
    Generate API calls dynamically based on the case description and SOP.
    """
    # Read SOP steps from file
    with open(sop_file, 'r') as file:
        sop_steps = file.read()

    # System prompt for dynamic API generation
    SYSTEM_PROMPT = """
    You are an intelligent assistant that automates ticket resolution using API calls.

    You will be provided with:
    1. A case description (what needs to be done)
    2. A list of relevant SOP steps (actions the user needs to take, such as creating a merchant, getting merchant info, etc.)

    Your task is to generate a structured list of API calls in JSON format to execute for the given case, based on the SOP steps.

    ### Available Actions:
    1. **Create Merchant** - To create a merchant.
    2. **Get Merchant Info** - To fetch the information about a merchant.
    3. **Update Merchant Details** - To update the merchant’s name or address.
    4. **Update Merchant Settings** - To update merchant settings (e.g., recurring billing, auto-settlement).

    ### Action Parameters:
    For each action, you will need to identify and extract the relevant parameters from the case description or SOP. You do not need to know the parameters explicitly in advance, as you will infer them from the case.

    ### Response Format:
    - Generate **only the necessary API calls** in the following format:
      {
        "api_calls": [
          {
            "method": "POST",
            "endpoint": "http://localhost:8000/api/merchant/create",
            "body": {
              "merchant_id": "12345",
              "name": "Merchant Name",
              "address": "Merchant Address"
            }
          },
          ...
        ]
      }

    ### Case:
    {case}

    ### SOP:
    {sop_steps}
    """

    # Prepare the prompt by inserting case and sop_steps dynamically
    prompt = SYSTEM_PROMPT.format(case=case, sop_steps=sop_steps)

    # Use the ollama.chat() function to interact with the LLM model
    response = ollama.chat(model="llama3.2", prompt=prompt)

    # Assuming the response from the model is a JSON string, we return it
    return json.loads(response)
