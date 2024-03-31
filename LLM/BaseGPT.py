import os.path

import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel

from interfaces import iAgent


class BaseGPT:
    def __init__(self, saveFile: str = "", agentFile="", source="gpt2", printProgress=False):
        localprint=lambda x:None
        if printProgress:
            localprint=print
        self.saveFile: str = saveFile
        self.agentFile: str = agentFile
        self.source: str = source

        self.tokenizer = None
        self.model = None
        tex,mex=False,False
        for (localsource,name) in [(saveFile,"save"),(agentFile,"agent base")]:
            if localsource:
                localprint("Attempting to load from {}...".format(name))
                temod,memod=self.LoadFromLocal(localsource,tex,mex)
                if temod:
                    self.tokenizer=temod
                if memod:
                    self.model=memod
                localprint(tex,mex)
        if not mex:
            localprint("Loading model from pretrained...")
            self.model = GPT2LMHeadModel.from_pretrained(source)
            input("Continue?")
            if saveFile:
                localprint("Saving model to {}...".format(saveFile))
                self.model.save_pretrained(saveFile)
        if not tex:
            localprint("Loading tokenizer from pretrained...")
            self.tokenizer = GPT2Tokenizer.from_pretrained(source)
            input("Continue?")
            if saveFile:
                localprint("Saving tokenizer to {}...".format(saveFile))
                self.tokenizer.save_pretrained(saveFile)
        return

    def LoadElement(self, origin: str, eltype:[GPT2LMHeadModel,GPT2Tokenizer], filename:str):
        if not os.path.exists(origin):
            return None

        path=os.path.join(origin, filename)

        exists=os.path.exists(path)
        if exists:
            return eltype.from_pretrained(origin)
        return None

    def LoadFromLocal(self, origin: str,tex,mex):
        if not os.path.exists(origin):
            return None,None

        X=[None,None]
        T=[tex,mex]
        I=[
            (origin, GPT2Tokenizer, "tokenizer_config.json"),
            (origin,GPT2LMHeadModel,"model.safetensors")
        ]
        for i,e in enumerate(I):
            if T[i]:
                continue
            X[i]=self.LoadElement(*e)
        return tuple(X)

    def __copy__(self):
        raise NotImplementedError


# Load pre-trained GPT-2 model and tokenizer
print("Importing...")
agent=BaseGPT("LARGE_LLM_data","gpt2",printProgress=True)
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
