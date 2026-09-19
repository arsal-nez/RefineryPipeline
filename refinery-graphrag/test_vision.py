import requests
import base64
import time

# =================================================================
# 👁️ OLLAMA VISION AI TESTER
# =================================================================

# 1. Set your model and image
MODEL_NAME = "moondream" # Try changing this to "llava-phi3" later!
IMAGE_PATH = r"image_95bbe2.jpg"  # Replace with the exact name of your blueprint image

def test_vision_ai():
    print(f"Loading {IMAGE_PATH}...")
    
    try:
        # Convert the image to Base64 so the AI can read it
        with open(IMAGE_PATH, "rb") as image_file:
            image_b64 = base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"❌ Could not find {IMAGE_PATH}. Make sure it is in the same folder as this script!")
        return

    # Setup the prompt for the AI
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": MODEL_NAME,
        "prompt": "You are an expert refinery engineer. Carefully look at this piping and instrumentation diagram. Tell me exactly what equipment, text, or process units you can see.",
        "stream": False,
        "images": [image_b64]
    }

    print(f"\n🧠 Asking {MODEL_NAME} to look at the blueprint...")
    print("⏳ Please wait. Vision models take heavy processing on a CPU...\n")
    
    start_time = time.time()
    
    # Send the image to Ollama
    response = requests.post(url, json=payload)
    
    end_time = time.time()
    
    # Print the results
    if response.status_code == 200:
        result = response.json().get("response", "")
        print("🤖 AI RESPONSE:")
        print("-" * 50)
        print(result.strip())
        print("-" * 50)
        print(f"⏱️ Time taken: {round(end_time - start_time, 1)} seconds")
    else:
        print(f"❌ Error: {response.text}")

if __name__ == "__main__":
    test_vision_ai()