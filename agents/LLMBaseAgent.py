import os.path

from transformers import GPT2Tokenizer, GPT2LMHeadModel

from interfaces import iAgent


class BaseGPTAgent(iAgent):
    def __init__(self, saveFile: str = "", agentFile="",source="gpt2",
                 modelType=GPT2LMHeadModel, tokenizerType=GPT2Tokenizer, printProgress=False, askInput=False):
        localprint=lambda x:None
        if printProgress:
            localprint=print
        self.saveFile: str = saveFile
        self.agentFile: str = agentFile
        self.source: str = source
        self.modelType=modelType
        self.tokenizerType=tokenizerType
        self.tokenizer = None
        self.model = None
        tex,mex=False,False
        if saveFile:
            localprint("Attempting to load from local...")
            tex,mex=self.LoadFromLocal(saveFile)
            localprint(tex,mex)
        if not mex:
            localprint("Loading model from pretrained...")
            self.model = self.modelType.from_pretrained(source)
            input("Continue?")
            if saveFile:
                localprint("Saving model to {}...".format(saveFile))
                self.model.save_pretrained(saveFile)
        if not tex:
            localprint("Loading tokenizer from pretrained...")
            self.tokenizer = self.tokenizerType.from_pretrained(source)
            input("Continue?")
            if saveFile:
                localprint("Saving tokenizer to {}...".format(saveFile))
                self.tokenizer.save_pretrained(saveFile)
        return

    def LoadFromLocal(self, origin: str):
        if not os.path.exists(origin):
            return False,False

        tokenizer_path = os.path.join(origin, "tokenizer_config.json")
        model_path = os.path.join(origin, "model.safetensors")

        tokenizer_exists=os.path.exists(tokenizer_path)
        model_exists=os.path.exists(model_path)
        if tokenizer_exists:
            self.tokenizer = self.tokenizerType.from_pretrained(origin)
        if model_exists:
            self.model = self.modelType.from_pretrained(origin)
        return tokenizer_exists,model_exists

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
agent=BaseGPTAgent("LARGE_LLM_data","gpt2",printProgress=True)
print("Done!")
# Define input text
input_text = input()
input_text = "Hello, how are you?" if not input_text else input_text

# Tokenize input text
input_ids = agent.tokenizer.encode(input_text, return_tensors="pt")
print(input_ids)

# Generate output sequence
output = agent.model.raw_init(input_ids, max_length=50, num_return_sequences=1)

# Decode and print output
generated_text = agent.tokenizer.decode(output[0], skip_special_tokens=True)
print(generated_text)


def main():
    return


if __name__ == "__main__":
    main()
