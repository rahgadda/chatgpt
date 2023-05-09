import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer

# Load pre-trained GPT-2 model and tokenizer
gpt2_model = GPT2LMHeadModel.from_pretrained('gpt2')
tokenizer = GPT2Tokenizer.from_pretrained('gpt2')

# Add padding token
tokenizer.add_special_tokens({'pad_token': '[PAD]'})
def generate_latent_vectors(input_sequences):
    input_ids = []
    attention_masks = []
    for sequence in input_sequences:
        encoded_dict = tokenizer.encode_plus(sequence, add_special_tokens=True, max_length=256, pad_to_max_length=True, return_attention_mask=True)
        input_ids.append(encoded_dict['input_ids'])
        attention_masks.append(encoded_dict['attention_mask'])
    input_ids = torch.tensor(input_ids)
    attention_masks = torch.tensor(attention_masks)
    with torch.no_grad():
        gpt2_output = gpt2_model(input_ids, attention_masks)[2][-2][:, -1, :]
    return gpt2_output.numpy()

def calculate_similarity(source_input_sequences, uploaded_input_sequences):
    # Generate latent vectors for source input sequences
    training_latent_vectors = generate_latent_vectors(source_input_sequences)
    
    # Generate latent vectors for uploaded input sequences
    uploaded_latent_vectors = generate_latent_vectors(uploaded_input_sequences)
    
    # Calculate cosine similarity between training and uploaded latent vectors
    similarity_scores = torch.nn.functional.cosine_similarity(torch.tensor(training_latent_vectors), torch.tensor(uploaded_latent_vectors), dim=1)
    return similarity_scores

# Example usage
source_file = '/workspace/chatgpt/02-dev/source_text.csv'
uploaded_file = '/workspace/chatgpt/02-dev/uploaded_text.csv'

# Load source and uploaded input sequences from csv files
import csv
with open(source_file, 'r') as f:
    reader = csv.reader(f)
    source_input_sequences = [row[0] for row in reader]
with open(uploaded_file, 'r') as f:
    reader = csv.reader(f)
    uploaded_input_sequences = [row[0] for row in reader]

# Calculate similarity scores
similarity_scores = calculate_similarity(source_input_sequences, uploaded_input_sequences)

# Print results
for i in range(len(similarity_scores)):
    print(f"Similarity score for uploaded file {i+1}: {similarity_scores[i]*100:.2f}%")