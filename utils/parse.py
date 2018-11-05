# index, token, lemma, dep, pos, tag, head, children = line.split('\t')

import numpy as np
import spacy
import json

nlp = spacy.load('en_core_web_lg', disable=['ner']) # ('en')

for line in open('coca.txt', 'r', encoding='utf8'):
    line = nlp(line.strip())
    for tk in line:
        children = [str(child.i) for child in tk.children]
        print(tk.i, tk.text, tk.lemma_, tk.dep_, tk.tag_, tk.pos_, tk.head.i, ','.join(children), sep='\t')
    print()
    