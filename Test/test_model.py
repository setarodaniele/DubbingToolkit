from transformers import MarianMTModel, MarianTokenizer

src = "it"
tgt = "ru"
model_name = f"Helsinki-NLP/opus-mt-{src}-{tgt}"

try:
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    model = MarianMTModel.from_pretrained(model_name)
    print("Modello disponibile")
except Exception as e:
    print("Modello NON disponibile:", e)
