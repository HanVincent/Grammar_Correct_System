import pickle
import spacy

nlp = spacy.load('en_core_web_lg') # ('en')

fs = open('../dataset/test.txt', 'r', encoding='utf8')
bnc_docs = nlp.pipe([line.strip().lower() for line in fs]) # minibatching - faster

doc_bytes = [doc.to_bytes(user_data=True) for doc in bnc_docs]
vocab_bytes = nlp.vocab.to_bytes()

with open("../dataset/bnc_processed.pickle","wb") as handle:
    pickle.dump((doc_bytes, vocab_bytes), handle)


