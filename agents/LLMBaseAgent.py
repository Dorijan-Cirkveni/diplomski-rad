import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel

from interfaces import iAgent


class GPTAgent(iAgent):
    def __init__(self):



# Load pre-trained GPT-2 model and tokenizer
print("Importing tokenizer...")
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
print("Importing model...")
model = GPT2LMHeadModel.from_pretrained("gpt2")
print("Done!")
# Define input text
input_text = input()
input_text = "Hello, how are you?" if not input_text else input_text

# Tokenize input text
input_ids = tokenizer.encode(input_text, return_tensors="pt")

# Generate output sequence
output = model.generate(input_ids, max_length=50, num_return_sequences=1)

# Decode and print output
generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
print(generated_text)

def main():
    return


if __name__ == "__main__":
    main()
