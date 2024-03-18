import os.path

import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel

from interfaces import iAgent


class BaseGPTAgent(iAgent):
    def __init__(self, saveFile: str = "", agentFile="", source="gpt2"):
        self.saveFile: str = saveFile
        self.agentFile: str = agentFile
        self.source: str = source
        self.tokenizer = None
        self.model = None
        if saveFile:
            self.LoadFromLocal(saveFile)
        if self.model is None:
            self.model = GPT2LMHeadModel.from_pretrained(source)
            if saveFile:
                self.model.save_pretrained(saveFile)
        if self.tokenizer is None:
            self.tokenizer = GPT2Tokenizer.from_pretrained(source)
            if saveFile:
                self.tokenizer.save_pretrained(saveFile)
        return

    def LoadFromLocal(self, origin: str):
        if not os.path.exists(origin):
            return False

        tokenizer_path = os.path.join(origin, "tokenizer_config.json")
        model_path = os.path.join(origin, "pytorch_model.bin")

        if not (os.path.exists(tokenizer_path) and os.path.exists(model_path)):
            return False

        self.tokenizer = GPT2Tokenizer.from_pretrained(origin)
        self.model = GPT2LMHeadModel.from_pretrained(origin)
        return True

    def receiveEnvironmentData(self, data):
        raise NotImplementedError

    def performAction(self, actions):
        raise NotImplementedError

    def submitDataEntry(self, entryKey) -> tuple[bool, object]:
        raise NotImplementedError

    def __copy__(self):
        raise NotImplementedError


# Load pre-trained GPT-2 model and tokenizer
print("Importing...")
agent=BaseGPTAgent("temp","gpt2")
print("Done!")
# Define input text
input_text = input()
input_text = "Hello, how are you?" if not input_text else input_text

# Tokenize input text
input_ids = agent.tokenizer.encode(input_text, return_tensors="pt")

# Generate output sequence
output = agent.model.generate(input_ids, max_length=50, num_return_sequences=1)

# Decode and print output
generated_text = agent.tokenizer.decode(output[0], skip_special_tokens=True)
print(generated_text)


def main():
    return


if __name__ == "__main__":
    main()
