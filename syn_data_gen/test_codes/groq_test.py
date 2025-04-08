import groq  # Ensure you have the correct library installed

# Initialize Groq Client
client = groq.Client(api_key="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")  # Replace with your actual API key

def generate_text(prompt, stream=False):
    """
    Generate text using Groq's Mixtral model.
    
    Args:
        prompt (str): The input prompt for the model.
        stream (bool): Whether to use streaming output.

    Returns:
        str: The generated response from the model.
    """
    print(f"\nGenerating response... (Stream: {stream})\n")

    messages = [{"role": "user", "content": prompt}]

    try:
        # API Call to Groq
        completion = client.chat.completions.create(
            model="mixtral-8x7b-32768",  # Ensure the model name is correct
            messages=messages,
            temperature=0.7,  # Adjust for randomness
            max_tokens=500,   # Reduce for quick testing
            top_p=1,
            stream=stream  # Toggle streaming
        )

        response_text = ""

        if stream:
            # Handle streaming output
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    response_text += chunk.choices[0].delta.content
                    print(chunk.choices[0].delta.content, end="", flush=True)  # Live streaming output
        else:
            # Handle normal response
            response_text = completion.choices[0].message.content
            print(response_text)

        print("\n\nDone generating response.")
        return response_text.strip()

    except Exception as e:
        print(f"⚠️ API Error: {e}")
        return None


# === TEST THE MODEL ===
if __name__ == "__main__":
    test_prompt = "Hello! How are you today?"
    
    # Test non-streaming mode
    print("\n--- Non-Streaming Mode ---")
    generate_text(test_prompt, stream=False)

    # Test streaming mode
    print("\n\n--- Streaming Mode ---")
    generate_text(test_prompt, stream=True)
