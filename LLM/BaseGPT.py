import json
import os.path

import GridStateEncoder
import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel

from interfaces import iAgent


class BaseGPT:
    def __init__(self, saveFile: str = "", agentFile="", source="gpt2", printProgress=False):
        self.printProgress:bool=printProgress
        self.saveFile: str = saveFile
        self.agentFile: str = agentFile
        self.source: str = source

        self.tokenizer = None
        self.model = None
        temod, memod=None,None
        for (localsource, name) in [(saveFile, "save"), (agentFile, "agent base")]:
            if localsource:
                self.print("Attempting to load from {}...".format(name))
                temod, memod = self.LoadFromLocal(localsource, None, None)
                self.print(temod is not None, memod is not None)
                if temod:
                    self.tokenizer = temod
                if memod:
                    self.model = memod
        if not temod:
            self.print("Loading tokenizer from pretrained...")
            self.tokenizer = GPT2Tokenizer.from_pretrained(source)
            input("Continue?")
            if saveFile:
                self.print("Saving tokenizer to {}...".format(saveFile))
                self.tokenizer.save_pretrained(saveFile)
        if not memod:
            self.print("Loading model from pretrained...")
            self.model = GPT2LMHeadModel.from_pretrained(source)
            input("Continue?")
            if saveFile:
                self.print("Saving model to {}...".format(saveFile))
                self.model.save_pretrained(saveFile)
        return

    def print(self,*args,**kwargs):
        if not self.printProgress:
            return
        return print(*args,**kwargs)

    def LoadElement(self, origin: str, eltype: [GPT2LMHeadModel, GPT2Tokenizer], filename: str):
        if not os.path.exists(origin):
            self.print(origin,"Path does not exist.")
            return None

        path = os.path.join(origin, filename)

        exists = os.path.exists(path)
        if exists:
            return eltype.from_pretrained(origin)
        return None

    def LoadFromLocal(self, origin: str, tex, mex):
        if not os.path.exists(origin):
            return None, None

        X = [None, None]
        T = [tex, mex]
        I = [
            (origin, GPT2Tokenizer, "tokenizer_config.json"),
            (origin, GPT2LMHeadModel, "model.safetensors")
        ]
        for i, e in enumerate(I):
            if T[i]:
                continue
            X[i] = self.LoadElement(*e)
        return tuple(X)

    def SaveTo(self,saveFile):
        self.print("Saving tokenizer to {}...".format(saveFile))
        self.tokenizer.save_pretrained(saveFile)
        self.print("Saving model to {}...".format(saveFile))
        self.model.save_pretrained(saveFile)

    def __copy__(self):
        raise NotImplementedError

    def InterpretInput(self,inputFull:dict):
        return json.dumps(inputFull)

def tensorTest():
    # Load pre-trained GPT-2 model and tokenizer
    print("Importing...")
    agent = BaseGPT("LARGE_LLM_data", "gpt2", printProgress=False)
    print("Done!")
    input_ids=GridStateEncoder.main()

    # Generate output sequence
    output = agent.model.generate(input_ids, max_length=100, num_return_sequences=1)

    # Decode and print output
    generated_text = agent.tokenizer.decode(output[0], skip_special_tokens=True)
    print(generated_text)



def main():
    # Load pre-trained GPT-2 model and tokenizer
    print("Importing...")
    agent = BaseGPT("LARGE_LLM_data", "gpt2", printProgress=False)
    print("Done!")
    # Define input text
    input_text = input()
    input_text = "Hello, how are you?" if not input_text else input_text

    # Tokenize input text
    input_ids = agent.tokenizer.encode(input_text, return_tensors="pt")

    # Generate output sequence
    output = agent.model.generate(input_ids, max_length=100, num_return_sequences=1)

    # Decode and print output
    generated_text = agent.tokenizer.decode(output[0], skip_special_tokens=True)
    print(generated_text)
    return


if __name__ == "__main__":
    tensorTest()
