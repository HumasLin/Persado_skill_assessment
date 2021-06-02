import re
import json
import nltk
import requests
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
  
lemmatizer = WordNetLemmatizer()
nltk.download('stopwords')

REGEX_URL = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

API_URL = "https://api-inference.huggingface.co/models/sshleifer/distilbart-cnn-12-6"
headers = {"Authorization": "Bearer api_KsWaOqjmMpBqNCvsVUtZlajFFwYfoOiLWZ"}

def query(text):
	data = json.dumps({"inputs": text})
	response = requests.request("POST", API_URL, headers=headers, data=data)
	return json.loads(response.content.decode("utf-8"))

def clean(text, lemma=0, join=1):
    #Remove non-letters
    no_url_text = re.sub(REGEX_URL," ",text)
    letters_only = re.sub("[^a-zA-Z ]", " ", no_url_text)
    
    #Convert to lower case and split
    words = letters_only.lower().split()
    
    #Covert stop words to a set
    stops = set(stopwords.words("english"))
    
    #Remove stopwords
    meaningful_words = [w for w in words if not w in stops]
    
    if lemma:
        meaningful_words=[lemmatizer.lemmatize(w) for w in meaningful_words]
    if join:
        #Join the words back into one string separated by space
        clean_text = " ".join(meaningful_words)
    else:
        clean_text = meaningful_words
        
    return clean_text
