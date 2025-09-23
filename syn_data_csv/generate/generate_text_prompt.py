# # generate_text_prompt.py
#
# from syn_data_csv.utils.constants import MAX_BATCH_SIZE
#
# def generate_prompt(config=None, ref_data=None, column_names=None, expected_columns=None, total_rows=None):
#
#     """Construct the LLM prompt dynamically."""
#     num_rows = MAX_BATCH_SIZE
#
#     user_prompt = ""
#     column_definitions = ""
#
#     if config:
#         # Extract user prompt and column definitions from config
#         user_prompt = config.get("prompt", [""])[0]
#         column_definitions = "\n".join(
#             [f"- {col['name']} ({col['type']})" for col in config.get('columns', [])]
#         )
#
#     if ref_data is not None and not ref_data.empty:
#         # Reference-only case or adding reference to config case
#         ref_preview = ref_data.head(3).to_csv(index=False)
#         if not config:
#             user_prompt = f"Generate synthetic data based on this reference sample:\n{ref_preview}"
#             column_definitions = ", ".join(ref_data.columns)
#         else:
#             user_prompt += f"\nAlso use the following reference data as format guidance:\n{ref_preview}"
#
#
#     prompt = f"""
#     Generate exactly {num_rows} unique rows of synthetic data in **CSV format only** with these columns:
#     {column_definitions}
#
#     **Rules:**
#     - 🚫 DO NOT include headers, explanations, summaries, or additional text.
#     - ✅ Output ONLY comma-separated values. No markdown. No bullets. No formatting.
#     - ✅ Each row must have exactly {expected_columns} fields — strictly match the column count.
#     - ✅ Strings should **NOT** be wrapped in quotes unless the string contains special characters (like commas or quotes) that require escaping. For example: `user101` ✅, not `"user101"` ❌.
#     - ✅ DO NOT say things like "And so on..." or "I've generated...".
#     - ✅ Do NOT wrap your response in code blocks (```, markdown).
#     - ✅ Do NOT add any trailing text, commentary, or notes after the rows.
#     - ✅ Each row must be unique. You must follow the realistic structure and values seen in reference data.
#
#     If reference data is provided, mimic its structure and values precisely.
#
#     Output:
#     - CSV only. No header. No explanation. Just raw comma-separated rows.
#     - **User instruction: {user_prompt}
#     """
#     return prompt.strip()


def generate_prompt(ref_data, num_rows):
    ref_preview = ref_data.head(3).to_csv(index=False)
    column_names = ", ".join(ref_data.columns)

    prompt = f"""
Generate exactly {num_rows} unique rows of synthetic data in CSV format
using the columns: {column_names}

Reference sample (first 3 rows):
{ref_preview}

Rules:
- No headers, explanations, or extra text
- Each row must have exactly {len(ref_data.columns)} fields
- Output only comma-separated values
- Each row must be unique
"""
    return prompt.strip()
