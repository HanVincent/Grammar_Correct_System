import spacy, pickle

nlp = spacy.load('en_core_web_lg') # ('en')

fs = open('../dataset/bnc.txt', 'r', encoding='utf8')
docs = [nlp(line.strip().lower()) for line in fs]

doc_bytes = [doc.to_bytes(user_data=True) for doc in docs]
vocab_bytes = nlp.vocab.to_bytes()


with open("../dataset/bnc_processed.pickle","wb") as handle:
    pickle.dump((doc_bytes, vocab_bytes), handle)

    
# # 讀取 pickle 並轉成 spacy class
# from spacy.tokens import Doc
# import pickle

# # Read parsed corpus
# with open("../dataset/bnc_processed.pickle", "rb") as handle:
#     doc_bytes, vocab_bytes = pickle.load(handle)
# nlp.vocab.from_bytes(vocab_bytes)
# docs = [Doc(nlp.vocab).from_bytes(b) for b in doc_bytes]