from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch

class Translator:
    def __init__(self, model_name="facebook/nllb-200-distilled-600M"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(self.device)

    def translate(self, text):
        self.tokenizer.src_lang = "hin_Deva"
        inputs = self.tokenizer(text, return_tensors="pt").to(self.device)
        translated_tokens = self.model.generate(
            **inputs,
            forced_bos_token_id=self.tokenizer.convert_tokens_to_ids("eng_Latn")
        )
        return self.tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]

if __name__ == '__main__':
    translator = Translator()
    hindi_text = "आप 'आयुष' नाम के बारे में जानकारी ढूंढ रहे हैं। यह एक लोकप्रिय भारतीय और हिंदू नाम है जिसका अर्थ है 'दीर्घायु', 'लंबा और स्वस्थ जीवन' या जीवन'। यह नाम सं                     स्कृत शब्द 'आयुस' से लिया गया है और इसका उपयोग अक्सर किसी व्यक्ति के लंबे और स्वस्थ जीवन की कामना के लिए किया जाता है"
    english_text = translator.translate(hindi_text)
    print(f"Hindi: {hindi_text}")
    print(f"English: {english_text}")
