#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from collections import defaultdict, Counter
from tqdm import tqdm

from utils.syntax import *
from utils.counts import *
# from utils.parse import parse


# In[ ]:


class DotDict(dict):
    
    def __getattr__(self, name):
        return self[name]
    
def construct(block):
    lines = [line for line in block.split('\n') if line]
    parsed = [ DotDict() for _ in range(len(lines)) ]

    for i, line in enumerate(lines):
        index, token, lemma, dep, tag, pos, head, children = line.split('\t')

        parsed[i].update({
            'i': int(index),
            'text': token,
            'lemma_': lemma,
            'dep_': dep,
            'pos_': pos,
            'tag_': tag,
            'head': parsed[int(head)],
            'children': [parsed[int(ch)] for ch in children.split(',') if ch],
            'doc': parsed
        })
        
    return parsed


# In[ ]:


# block = '''0	we	-PRON-	nsubj	PRP	PRON	1	
# 1	want	want	ROOT	VBP	VERB	1	0,3
# 2	to	to	aux	TO	PART	3	
# 3	discuss	discuss	xcomp	VB	VERB	1	2,4
# 4	something	something	dobj	NN	NOUN	3	'''

# entry = construct(block)


# In[ ]:


import gzip

fs = gzip.open('../coca.spacy.dep.txt.gz', 'rt', encoding='utf8')
contents = fs.read().split('\n\n')


# In[ ]:


patterns = defaultdict(lambda: defaultdict(Counter))
ngrams = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [])))
sents = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [])))
    
def retrieve_dep(entry):
    sent = ' '.join([tk.text for tk in entry])

    if len(entry) > 30: return # skip long sentence
    if '@@@' in sent: return

    sent_score = score(sent)
    
    for token in entry:
        if token.tag_ in POS['VERB']: # or tag == VERB
            ptn_tks, ngram_tks = dep_to_ptns_ngrams(token)
            ptn, ngram = ' '.join(ptn_tks), ' '.join(ngram_tks)

            patterns[token.lemma_][token.dep_][ptn] += 1
            ngrams[token.lemma_][token.dep_][ptn].append(ngram)
            sents[token.lemma_][token.dep_][ptn].append((sent, sent_score))
            
        elif token.tag_ in POS['ADJ']:
            pass
        elif token.tag_ in POS['NOUN']:
            pass


# In[ ]:


for entry in tqdm(contents):
    retrieve_dep(construct(entry))


# ### Minimize Ngrams and Sentences
# * ngrams count < 10
# * top 100 common sentences

# In[ ]:


slim_patterns = defaultdict(lambda: defaultdict(Counter))
slim_ngrams = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [])))
slim_sents = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [])))

for word in patterns:
    for dep in patterns[word]:
        
        truncated_ptns = truncate_k(patterns[word][dep], 10) # remove pattern whose count <= 10
        
        for ptn, cnt in truncated_ptns.items():
            slim_patterns[word][dep][ptn] = cnt
            
            slim_ngrams[word][dep][ptn].extend(ngrams[word][dep][ptn])
            
            sorted_sents = sort_dict(sents[word][dep][ptn])
            slim_sents[word][dep][ptn].extend([s for (s, sent_score) in sorted_sents[:100]])


# ### Save in json file
# #### TODO: store in sqlite?

# In[ ]:


import json

with open('static/data/coca.patterns.slim.json', 'w', encoding='utf8') as ws:
    json.dump({ 'patterns': slim_patterns, 'ngrams': slim_ngrams, 'sents': slim_sents }, ws)


# In[ ]:


# patterns['discuss'].keys()


# In[ ]:


# patterns['discuss']['ROOT']

