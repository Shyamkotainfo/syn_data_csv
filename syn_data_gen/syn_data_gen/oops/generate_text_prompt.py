import json


class PromptGenerator:
    """Constructs and generates prompts for LLM-based synthetic data generation."""

    @staticmethod
    def create_prompt(config, reference_samples):
        num_rows = config.get("num_rows", 100)
        user_prompt = config.get("prompt", [""])[0]  # Extract user-given text
        column_definitions = "\n".join(
            [f"- {col['name']} ({col['type']})" for col in config.get('columns', [])]
        )

        prompt = f"""
        Generate {num_rows} rows of synthetic data in CSV format with these columns:
        {column_definitions}

        **Rules:**
        - Data format: CSV only.
        - Rows must be unique; columns need not be unique.
        - Include at least one primary key.
        - Ensure the data follows a realistic pattern.
        - **Replicate the pattern in reference data**
        - Take count of rows from the user instruction.
        - **Each row must contain exactly {len(config.get("columns", []))} values. No missing or extra fields.**
        - **Output format: Only comma-separated values (NO HEADER, NO EXTRA TEXT).**
        - **Ensure CSV output has NO extra text, NO headers, NO extra spacing, and is STRICTLY comma-separated.**
        - **No excessive quotation marks unless necessary for escaping commas in text fields.**
        - If the user requests grouping, format the data in a way that allows SQL-style grouping.
        
        """
        if reference_samples:
            prompt += f"""
        **Reference Data Examples:**
        {json.dumps(reference_samples, indent=4)}
        
        - Ensure the generated data follows this structure.
        """
        return prompt.strip()

    @staticmethod
    def generate_text(prompt, client):
        """Generate text using Groq's Mixtral model."""
        messages = [{"role": "user", "content": prompt}]
        completion = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=messages,
            temperature=1,
            max_tokens=6000,
            top_p=1,
            stream=True
        )
        response_text = "".join(chunk.choices[0].delta.content for chunk in completion if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content)
        return response_text.strip()
