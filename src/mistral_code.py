import sys
from flask import Flask, request, Response
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load Model & Tokenizer
model_name = "mistralai/Mistral-7B-Instruct-v0.1"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16, device_map="auto")

generated_set = set()  # Store generated rows to ensure uniqueness

def format_value(value, col_type):
    """Format values based on column type."""
    if col_type == "int":
        return str(int(value))
    elif col_type == "float":
        return f"{float(value):.1f}"
    elif col_type == "boolean":
        return str(value).lower()
    return f'"{value}"'  # Strings enclosed in quotes

def process_csv_output(text, column_types, headers):
    """Extract valid CSV rows from model response."""
    lines = text.strip().split("\n")
    csv_rows = set()

    for line in lines:
        values = [x.strip().strip('"') for x in line.split(",")]

        if values == headers or len(values) != len(column_types):
            continue  # Skip headers or malformed rows

        formatted_row = ",".join(format_value(v, t) for v, t in zip(values, column_types))
        csv_rows.add(formatted_row)

    return csv_rows

def generate_csv(columns, rows_count):
    """Generate structured CSV using LLM."""
    headers = [col["name"] for col in columns]
    header_line = ",".join(f'"{col}"' for col in headers)
    column_types = [col["type"] for col in columns]

    yield (header_line + "\n").encode("utf-8")  # Send headers first
    sys.stdout.flush()

    total_generated = 0
    retry_attempts = 3  # Allow retries for missing rows

    while total_generated < rows_count:
        batch_size = min(500, rows_count - total_generated) 

        prompt = (
            f"Generate {batch_size} unique rows of structured CSV data. "
            f"Columns: {', '.join(f'{col['name']} ({col['type']})' for col in columns)}. "
            f"Ensure correct data types. Output only CSV rows, no explanations."
        )

        inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
        outputs = model.generate(**inputs, max_new_tokens=6000)  # Generate more rows per call
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        unique_rows = process_csv_output(generated_text, column_types, headers)
        new_rows = unique_rows - generated_set  # Remove duplicates

        if new_rows:
            chunk = "\n".join(new_rows) + "\n"
            yield chunk.encode("utf-8")  # Stream output
            sys.stdout.flush()
            generated_set.update(new_rows)
            total_generated += len(new_rows)
        elif retry_attempts > 0:  # Retry if not enough new rows
            retry_attempts -= 1
            continue
        else:
            break  # Stop if retries are exhausted

@app.route("/generate", methods=["POST"])
def generate_text():
    """API Endpoint to generate CSV based on user-defined schema."""
    data = request.json
    columns = data.get("columns", [])
    rows_count = data.get("rows_count", 1000)  # Default 1000 rows

    if not columns or rows_count <= 0:
        return Response("Invalid input data", status=400)

    return Response(generate_csv(columns, rows_count), mimetype="text/csv", direct_passthrough=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)
