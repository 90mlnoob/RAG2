# tools.py
import json

def call_api(action_input: dict) -> str:
    try:
        endpoint = action_input["endpoint"]
        method = action_input["method"]
        payload = action_input["payload"]

        # Parse payload if it's a string
        if isinstance(payload, str):
            payload = json.loads(payload)

        print(f"✅ API CALL to {endpoint} with method {method} and payload: {payload}")
        
        # Simulate a real response
        return f"✅ Success: {endpoint} API called with payload: {json.dumps(payload)}"

    except Exception as e:
        return f"❌ API call failed: {str(e)}"
