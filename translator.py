from transformers import MarianMTModel, MarianTokenizer
import torch

class Translator:
    def __init__(self, model_name="Helsinki-NLP/opus-mt-hi-en"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = MarianTokenizer.from_pretrained(model_name)
        self.model = MarianMTModel.from_pretrained(model_name).to(self.device)

    def translate(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", padding=True).to(self.device)
        translated = self.model.generate(**inputs)
        return [self.tokenizer.decode(t, skip_special_tokens=True) for t in translated][0]

if __name__ == '__main__':
    translator = Translator()
    hindi_text = "आपका स्वागत है"
    english_text = translator.translate(hindi_text)
    print(f"Hindi: {hindi_text}")
    print(f"English: {english_text}")
