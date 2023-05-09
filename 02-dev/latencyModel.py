import csv
import torch
from transformers import GPTNeoForCausalLM, GPT2Tokenizer

# Load tokenizer and model
print("Loading model")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_name = "EleutherAI/gpt-neo-2.7B"
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPTNeoForCausalLM.from_pretrained(model_name)

config = model.config
config.n_embd = 2560
config.n_head = 20
config.n_layer = 32

print("Update config and reload model")
model = GPTNeoForCausalLM(config)
model.resize_token_embeddings(len(tokenizer))
model.to(device)

# Load source file and convert to list of dictionaries
print("Reading Source Data")
with open('/workspace/chatgpt/02-dev/source_text.csv') as f:
    reader = csv.DictReader(f)
    source_data = [row for row in reader]

# Create a list of all column names in the source data
source_column_names = [col.lower() for col in source_data[0].keys()]

# Load input file and convert to list of dictionaries
print("Reading Upload Data")
with open('/workspace/chatgpt/02-dev/uploaded_text.csv') as f:
    reader = csv.DictReader(f)
    input_data = [row for row in reader]

# Compare column names in input data with column names in source data
print("Comparing Data")
for input_row in input_data:
    input_column_names = [col.lower() for col in input_row.keys()]
    similarity = sum([1 for col in input_column_names if col in source_column_names]) / len(input_column_names)
    print(f"Similarity: {similarity:.2%}")

# pip install torch transformers