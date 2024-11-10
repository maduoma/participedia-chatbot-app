# text_utils.py
from nltk.tokenize import sent_tokenize


def capitalize_sentences(text):
    sentences = sent_tokenize(text)
    capitalized_sentences = [sentence.capitalize() for sentence in sentences]
    return ' '.join(capitalized_sentences)
