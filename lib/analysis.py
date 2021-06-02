import re
import nltk
import spacy
import numpy as np
from lib.utils import *
from io import BytesIO
from wordcloud import WordCloud
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer

nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')

def get_most_used_words(document):
    count = Counter(" ".join([text for text in document]).split())
    most_occur = count.most_common(10)
    return np.array(most_occur)

def get_tfidf_top_features(documents,n_top=10):
    tfidf_vectorizer = TfidfVectorizer(max_df=0.95, min_df=2,stop_words='english')
    tfidf = tfidf_vectorizer.fit_transform(documents)
    importance = np.argsort(np.asarray(tfidf.sum(axis=0)).ravel())[::-1]
    tfidf_feature_names = np.array(tfidf_vectorizer.get_feature_names())
    return tfidf_feature_names[importance[:n_top]]

def plot_wordcloud(data):
    wordcloud = WordCloud(width = 1600, height = 600, 
                background_color ='white', 
                stopwords = set(stopwords.words("english")), 
                min_font_size = 12).generate(" ".join(data))
    return wordcloud.to_image()

