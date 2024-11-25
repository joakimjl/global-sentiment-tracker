from transformers import AutoModelForSequenceClassification
from transformers import AutoTokenizer, AutoConfig
import numpy as np
from scipy.special import softmax
# Preprocess text (username and link placeholders)
# Model credit goes to: https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment-latest

class GST_Roberta:
    def __init__(self) -> None:
        MODEL = f"cardiffnlp/twitter-roberta-base-sentiment-latest"
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL)
        self.config = AutoConfig.from_pretrained(MODEL)
        self.model = AutoModelForSequenceClassification.from_pretrained(MODEL)
    
    def preprocess(self, text):
        new_text = []
        for t in text.split(" "):
            t = '@user' if t.startswith('@') and len(t) > 1 else t
            t = 'http' if t.startswith('http') else t
            new_text.append(t)
        return " ".join(new_text)

    def roberta_process_batch(self, text_arr):
        score_arr = []
        for text in text_arr:
            encoded_input = self.tokenizer(text, return_tensors='pt')
            output = self.model(**encoded_input)
            scores = output[0][0].detach().numpy()
            scores = softmax(scores)
            scores = np.round(scores, 4)
            #print(f'{text}: neg: {str(scores[0])[0:6]} neu: {str(scores[1])[0:6]} pos: {str(scores[2])[0:6]}')
            score_arr.append(scores)
        return score_arr



if __name__ == "__main__":
    roberta = GST_Roberta()
    #Testing for country name bias, seems to be in the berta model
    roberta.roberta_process_batch(["I like cookies", 
                                   "China is a country", 
                                   "America is a country",
                                   "Sweden is a country",
                                   "Phillipines is a country",
                                   "Ireland is a country"])

    """
    MODEL = f"cardiffnlp/twitter-roberta-base-sentiment-latest"
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    config = AutoConfig.from_pretrained(MODEL)
    # PT
    model = AutoModelForSequenceClassification.from_pretrained(MODEL)
    #model.save_pretrained(MODEL)
    text = "Covid cases are increasing fast!"
    text = preprocess(text)
    encoded_input = tokenizer(text, return_tensors='pt')
    output = model(**encoded_input)
    scores = output[0][0].detach().numpy()
    scores = softmax(scores)
    ranking = np.argsort(scores)
    ranking = ranking[::-1]
    print(scores[ranking])
    for i in range(scores.shape[0]):
        l = config.id2label[ranking[i]]
        s = scores[ranking[i]]
        print(f"{i+1}) {l} {np.round(float(s), 4)}")"""
