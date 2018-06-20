
# coding: utf-8

# In[1]:


from collections import defaultdict, Counter
from nltk.metrics.distance import edit_distance
from operator import itemgetter
from Bio import pairwise2
from utils.syntax import *
from utils.counts import *
import numpy as np
import spacy
import json


# In[2]:


nlp = spacy.load('en_core_web_lg') # ('en')


# In[3]:


# Read patterns/sents json file
with open('static/data/coca.json', 'r', encoding='utf8') as fs:
    BNC = json.load(fs)
    patterns, sents, ngrams = BNC['patterns'], BNC['sents'], BNC['ngrams']


# In[4]:


def normalize(ptn):
    if 'be V-ed' in ptn: print(ptn) # 先不管被動用法
            
    ptn = 'V' + ptn.split('V')[1] # 去頭 (headword 之前的)
    ptn = ' '.join(ptn.split(' ')[:4]) # max lenght: 4-gram
    ptn = ptn.replace('V-ing', 'V').replace('V-ed', 'V') # 除了被動外，完成式和進行式改成原 V
    # ptn = ptn.replace('wh-cl', 'O').replace('cl', 'O') # cl / wh-cl -> O
    # ptn = ptn.replace('to-v', 'ADJ').replace('v-ing', 'ADJ') # v-ing / to-v -> ?
        
    # if / which / who / whom
    # TODO: 還要修改條件？
    ptn = ptn.split(' ')
    if len(ptn) > 2:
        if ptn[1] in PREPOSITIONS: # V prep. _
            ptn = ptn[:3]
        elif ptn[1] != 'O': # V before O
            ptn = ptn[:1]
        elif ptn[2] in PREPOSITIONS: # V O prep. O
            ptn = ptn[:4]
        else: # V O O / V O not_prep
            ptn = ptn[:2]
    return ' '.join(ptn)


norm_patterns = defaultdict(lambda: defaultdict(Counter))
norm_ngrams = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [])))
norm_sents = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [])))

for headword in patterns:
    for dep in patterns[headword]:
        for ptn in patterns[headword][dep]:
            norm_patterns[headword][dep][normalize(ptn)] += patterns[headword][dep][ptn]
            norm_ngrams[headword][dep][normalize(ptn)].extend(ngrams[headword][dep][ptn])
            norm_sents[headword][dep][normalize(ptn)].extend(sents[headword][dep][ptn])


# In[94]:


# 使用 ptn / first_ptn 百分比
def predict_ratio(ptn, patterns):
    if ptn not in patterns: 
        return 0
    return patterns[ptn] / patterns[max(patterns, key=patterns.get)]
    
CONFIDENT, UNCONFIDENT = 0.2, 0.1

def categorize(ratio):
    if ratio > CONFIDENT:     return 'right'
    elif ratio < UNCONFIDENT: return 'wrong'
    else:                     return 'not_sure'
    
    
def get_template(ratio):
    if ratio > CONFIDENT:     return '{{+{}+}}'
    elif ratio < UNCONFIDENT: return '[-{}-]'
    else:                     return '\\*{}*\\'
    
    
def suggest_ptn(bad_ptn, ptns):
    ptns = truncate_k(ptns, ptns[bad_ptn]) if bad_ptn in ptns else ptns # Optimize if exist

    sim_ptns = sorted(ptns, key=ptns.get, reverse=True)
    sim_ptns = sorted(sim_ptns, key=lambda ptn: edit_distance(bad_ptn.split(' '), ptn.split(' ')))
    
#     print(sim_ptns[:5])
    
    return sim_ptns[0]


def suggest_ngram(ngram, ngrams):
    ngrams = filter(lambda ng: '@@@' not in ng, set(ngrams)) # workaround
    ngram = ngram.lower()

    sim_ngrams = sorted(ngrams, key=lambda ng: edit_distance(ngram.split(' '), ng.split(' ')))
    
#     print(sim_ngrams[:5])
    
    return sim_ngrams[0]


def edit_ngram(tk, ngram_list, old_ptn, new_ptn):
    edit_ngram_list = [ng.text for ng in ngram_list]
    old_ptn, new_ptn = old_ptn.split(' '), new_ptn.split(' ')
    align = pairwise2.align.globalxs(old_ptn, new_ptn, -10, -0.5, gap_char=['_'])[0]
    anchor = [i for i, ng in enumerate(ngram_list) if ng.i == tk.i][0]
    
    for i, tag in enumerate(align[1]):
        if tag in ['S', 'V', 'O']: 
            pass
        elif tag in PREPOSITIONS and edit_ngram_list[i+anchor] in PREPOSITIONS: 
            edit_ngram_list[i + anchor] = tag
        elif tag in PREPOSITIONS:
            edit_ngram_list[i + anchor] = tag + ' ' + edit_ngram_list[i + anchor]
        elif tag == '_': 
            edit_ngram_list[i + anchor] = None
        else:
            print("Not here:", tag)

    return ' '.join([ng for ng in edit_ngram_list if ng])


def edit_sentence():
    pass


def correct(line):
    line = nlp(line)
    
    edits, suggestions, edit_line = [], [], [tk.text for tk in line]
    for tk in line:
        if tk.tag_ in POS['VERBS']:
            # 以下拆 def ?
            ptns, ngrams = dep_to_ptns_ngrams(tk)
            ptn, ngram = ' '.join(ptns), ' '.join([ng.text for ng in ngrams])
            # print("ptn: {}, ngram: {}".format(ptn, ngram))
            
            norm_ptn = normalize(ptn)
            ptns = norm_patterns[tk.lemma_][tk.dep_]
            # high_ptns  = get_high_freq(ptns)
            
            ratio = predict_ratio(norm_ptn, ptns)
            # print(tk.text, tk.dep_, norm_ptn, ratio)
        
            if ratio < CONFIDENT:
                top_ptn = suggest_ptn(norm_ptn, ptns)
                top_ngram = suggest_ngram(ngram, norm_ngrams[tk.lemma_][tk.dep_][top_ptn])
                new_ngram = edit_ngram(tk, ngrams, norm_ptn, top_ptn)
            
                suggestions.append({
                    'category': categorize(ratio),
                    'tk': tk.text,
                    'bef': norm_ptn,
                    'aft': top_ptn,
                    'ngram': new_ngram
                    # 'ngram': top_ngram
                })

            edits.append(get_template(ratio).format(tk.text))
        else:
            edits.append(tk.text)
   
    return ' '.join(edits), suggestions

def main_process(content):
    edit_lines, suggestions = [], []

    for line in content.split('\n'):
        edit, sug = correct(line)
        
        edit_lines.append(edit)
        suggestions.extend(sug)

    return edit_lines, suggestions
 


# In[97]:


if __name__ == '__main__':
    from pprint import pprint
#     user_input = '''I want to discuss exaggerately about my life. I rely my ability.'''
    user_input = 'can you rely heavily in my life in last July without hestitation?'
    pprint(main_process(user_input))


# In[1]:


#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin

app = Flask(__name__)

app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app)


@app.route('/')
def index():
    return render_template('index.html')


# post /correct data: {content :}
@app.route('/correct' , methods=['POST'])
def start_correct():
    request_data = request.get_json()
    if not request_data: return jsonify({'edit': 'Should not be empty'})
    
    content = request_data['content']
    print(content)
    
    edits, suggestions = main_process(content)
    
    return jsonify({
        'edits': edits,
        'suggestions': suggestions
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=1314)

