import os
import sys


# Add the current directory to sys.path to make sure imports work
sys.path.append(os.getcwd())

try:
    from app.models import Input_Query
    # Replace 'app.services' with the actual file name where ai_request is defined
    from app.utils.ai_calling import ai_request 
except ImportError as e:
    print("Error importing modules. Make sure you are running this from the root directory.")
    print(f"Details: {e}")
    exit(1)

def run_manual_test():
    # 1. Check for API Key

    print("--- Preparing Request ---")
    
    # CRITICAL: Ensure your Input_Query model definition matches the field names 
    # used in ai_request. Your function uses 'request.type', so I am using 'type' here.
    input_data = Input_Query(
        type="Translation",  # Or 'temperature' if you stick to the old model name
        system_prompt="You are a JSON generator. You always return JSON with a 'response' key.",
        user_query="Translate 'Hello World' to Spanish."
    )
    
    print(f"Type: {input_data.type}")
    print(f"System Prompt: {input_data.system_prompt}")
    print(f"User Query: {input_data.user_query}")

    # 3. Call the API
    print("\n--- Sending Request to DeepSeek (Real API Call) ---")
    try:
        # This calls the actual function without mocks
        result = ai_request(input_data)
        
        print("\n✅ Request Successful!")
        print("--- API Response ---")
        print(f"Response Text: {result.response}")
        print(f"Error Status: {result.error}")
        print(f"Full Dump: {result.model_dump()}")

    except Exception as e:
        print("\n❌ Request Failed!")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {e}")
        print(result.response)
        
        # Debugging hints for specific errors
        if "AttributeError" in str(e):
            print("\n[Hint] Check if 'request.type' in your function matches 'temperature' in your Pydantic model.")
        if "ValidationError" in str(e):
            print("\n[Hint] The API returned JSON, but it didn't match Output_Response (missing 'response' field?).")
            print("Note: Your current ai_request implementation hardcodes the messages to 'Hello'.") 
            print("It ignores the input prompts, so the AI might not know to return the correct JSON format.")

if __name__ == "__main__":
    run_manual_test()