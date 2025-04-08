import json



def generate_prompt(config, reference_samples):
    """Construct the LLM prompt dynamically."""
    num_rows = config.get("num_rows", 100)
    user_prompt = config.get("prompt", [""])[0]  # Extract user-given text
    column_definitions = "\n".join(
        [f"- {col['name']} ({col['type']})" for col in config.get('columns', [])]
    )

    prompt = f"""
    Generate {num_rows} unique rows of synthetic data in CSV format with these columns:
    {column_definitions}

    **Rules:**

    - Data format: CSV only.
    - Rows must be unique; columns need not be unique.
    - Include at least one primary key.
    - Ensure the data follows a realistic pattern.
    - Strings shouldn't be in quotes. Ex: ('""user101"" -->incorrect, user101  --> correct)
    - **Replicate the pattern in reference data**
    - Take count of rows form the user instruction.
    - **Each row must contain exactly {len(config.get("columns", []))} values. No missing or extra fields.**
    - **Output format: Only comma-separated values (NO HEADER, NO EXTRA TEXT).**'
    - **Ensure CSV output has NO extra text, NO headers, NO extra spacing, and is STRICTLY comma-separated.**
    - **No excessive quotation marks unless necessary for escaping commas in text fields.**



    ----
    - User instruction: {user_prompt}
    """

    if reference_samples:
        prompt += f"""
    **Reference Data Examples:**
    {json.dumps(reference_samples, indent=4)}

    - Ensure the generated data follows this structure.
    """

    return prompt.strip()


def generate_text(prompt, client):

    """Generate text using Groq's Mixtral model."""
    messages = [{"role": "user", "content": prompt}]
    
    # Call Groq API for text generation
    completion = client.chat.completions.create(
        model="mistral-saba-24b",
        messages=messages,
        temperature=1,
        max_tokens=6000,
        top_p=1,
        stream=True
    )

    # Capture streamed output
    response_text = ""
    for chunk in completion:
        if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
            response_text += chunk.choices[0].delta.content

    return response_text.strip()
