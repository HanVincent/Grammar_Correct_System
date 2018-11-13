#!/usr/bin/env python
# coding: utf-8

# In[2]:


from collections import defaultdict, Counter

from utils.counts import *
from utils.syntax import *

import sqlite3
import spacy
import json, math


# In[1]:


nlp = spacy.load('en_core_web_lg') # ('en')


# In[4]:


conn = sqlite3.connect('static/data/rules.db', check_same_thread=False)
cursor = conn.cursor()


# In[33]:


# Use ptn / first_ptn ratio
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
    if ratio > CONFIDENT:     return '{{+{}//{}+}}'
    elif ratio < UNCONFIDENT: return '[-{}//{}-]'
    else:                     return '\\*{}//{}*\\'
    

def edit(line):
    line = nlp(line)

    edits, meta = [], {}
    for i, tk in enumerate(line):
        if tk.tag_ in POS['VERB']:
            ptns, ngrams = dep_to_ptns_ngrams(tk)
            ptn, ngram = ' '.join(ptns), ' '.join(ngrams)
            
            norm_ptn = normalize(ptn)
            
            ptns_counts_cur = cursor.execute("SELECT norm_ptn, SUM(count) FROM rules WHERE word=? AND dep=? GROUP BY norm_ptn", 
                                         (tk.lemma_, tk.dep_))
            ptns_counts = dict(ptns_counts_cur.fetchall())
          
            ratio = predict_ratio(norm_ptn, ptns_counts)
         
            meta[str(i)] = {
                'lemma': tk.lemma_,
                'dep': tk.dep_,
                'bef': norm_ptn,
                'ngram': ngram
            }

            edits.append(get_template(ratio).format(tk.text, i))
        else:
            edits.append(tk.text)
   
    return ' '.join(edits), meta


def suggest_ptns(bad_ptn, all_ptns, k=5):
    ptns = truncate_k(all_ptns, all_ptns[bad_ptn]) if bad_ptn in all_ptns else all_ptns # Optimize if exist
    
    if len(ptns) == 0:
        return sort_dict(all_ptns)[:k]
        
    bad_ptn_tks = bad_ptn.split(' ')
    sim_ptns = sort_dict(ptns)
    sim_ptns = sorted(sim_ptns, key=lambda ptn: edit_distance(bad_ptn_tks, ptn.split(' ')))
    
    return sim_ptns[:k]


def suggest_ngrams(ngram, ngrams):
    ngram = ngram.lower()
    ngram_tks = ngram.split(' ')
    
    sim_ngrams = sorted(ngrams, key=lambda ng: edit_distance(ngram_tks, ng.split(' ')))
    
    return sim_ngrams[:3]


def suggest_info(data):
    '''{
        'lemma': tk.lemma_,
        'dep': tk.dep_,
        'bef': norm_ptn,
        'ngram': ngram
    }'''
    info = []
    
    ptns_counts_cur = cursor.execute("SELECT norm_ptn, SUM(count) FROM rules WHERE word=? AND dep=? GROUP BY norm_ptn", 
                                 (data['lemma'], data['dep']))
    ptns_counts = dict(ptns_counts_cur.fetchall())

    ptns = suggest_ptns(data['bef'], ptns_counts)
    
    total = sum(ptns_counts.values())
    
    for ptn in ptns:
        ngrams_cur = cursor.execute("SELECT ngrams FROM rules WHERE word=? AND dep=? AND norm_ptn=?", 
                                 (data['lemma'], data['dep'], ptn))
        ngrams = [ each for ngram_str in ngrams_cur.fetchall() for each in json.loads(ngram_str[0])]

        ngrams = suggest_ngrams(data['ngram'], ngrams)

        per = ptns_counts[ptn] / total
    
        if per < 0.01: continue
    
        info.append({'ptn': ptn, 'percent': math.floor(per*100),'ngrams': ngrams})
    return info


def edit_ngram():
    pass


def edit_sentence():
    pass


# In[34]:


if __name__ == '__main__':
    from pprint import pprint
    from utils.counts import *
    
    user_input = '''I like you. \n I want discuss exaggerately about my life. I rely my ability.'''
#     user_input = 'can you rely heavily in my life in last July without hestitation?'
    pprint(edit(user_input))
    print()
    pprint(suggest_info({'tk': 'rely', 'ngram': 'I rely ability', 'bef': 'V O', 'dep': 'ROOT', 'lemma': 'rely'}))
#     pprint(suggest_info({'tk': 'discuss', 'ngram': 'to discuss about life', 'bef': 'V about O', 'dep': 'xcomp', 'lemma': 'discuss'}))
#     pprint(suggest_info({'bef': 'V to-v', 'dep': 'ROOT', 'ngram': 'I want discuss', 'lemma': 'want'}))


# In[ ]:


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


# post /correct data: { content: str }
@app.route('/correct', methods=['POST'])
def correct():
    request_data = request.get_json()
    if not request_data: return jsonify({'edit': 'Should not be empty'})
    
    content = request_data['content']
    print(content)
        
    edit_line, meta = edit(content)

    return jsonify({'edit': edit_line, 'meta': meta})


# post /suggest data: {'tk': 'want', 'bef': 'V to-v', 'dep': 'ROOT', 'lemma': 'want'}
@app.route('/suggest', methods=['POST'])
def suggest():
    request_data = request.get_json()
    if not request_data: return jsonify({'edit': 'Should not be empty'})
    
    print(request_data)
    
    return jsonify({'info': suggest_info(request_data)})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=1315)
    cursor.close()


# In[ ]:




