# coding: utf-8

from utils.syntax import *
from collections import defaultdict, Counter
import numpy as np
import spacy
import json

nlp = spacy.load('en_core_web_lg') # ('en')


# ## 用 dependency 抓 pattern
# #### 第一層 dependency
# dobj, prep, nsubj, nsubjpass, ccomp, xcomp, csubj, csubjpass, prt, acomp, oprd

# #### 第二層 dependency
# prep -> pobj, pcomp


def clean_data(file):
    lower_lines = map(lambda line: line.strip().lower(), open(file, 'r', encoding='utf8'))
    lines = filter(lambda line: len(line.split(' ')) <= 25, lower_lines)
    return lines


if __name__ == '__main__':
    # Head word only VERBS
    # headword, patterns, dep, ngrams
    patterns = defaultdict(lambda: defaultdict(Counter))
    ngrams = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [])))
    sents = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: []))) # for debug

    file_name = 'coca' # 'bnc'
    
    for line in clean_data('../dataset/' + file_name + '.txt'):
        line = nlp(line, disable=['ner'])
        for tk in line:
            if tk.tag_ in VERBS: 
                ptn, ngram = dep_to_pattern(tk)

                patterns[tk.lemma_][tk.dep_][ptn] += 1
                ngrams[tk.lemma_][tk.dep_][ptn].append(ngram)
                sents[tk.lemma_][tk.dep_][ptn].append(tk.doc.text)


    with open(file_name + '.json', 'w', encoding='utf8') as ws:
        json.dump({ 'patterns': patterns, 'ngrams': ngrams, 'sents': sents }, ws)


