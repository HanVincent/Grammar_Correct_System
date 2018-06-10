import nltk, re, sys
import fileinput
from collections import Counter

def to_after(tokens):
    def to_after_token(token):
        token = token.replace('\u3000', ' ')
        if token == ' ': return ''
        
        if token.endswith('-]'):
            return None
        
        # 保留字邏輯區，但是可能有誤，像是 is+} 可能抓到 his+}
        elif reserved and (token.endswith(reserved + '+}') or token.startswith('[-' + reserved)):
            # 丟掉多於一個單字的，目前是 before/after 都丟
            return token[token.rfind('>>')+2:-2] if ' ' in token else token
        
        elif token.endswith('+}'):
            return token[token.rfind('>>')+2:-2]  if token.startswith('[-') else token[2:-2]  
        else:
            return token
        
    tokens = [e for token in map(to_after_token, tokens) if token for e in token.split(' ')]
    indices = [i for i, t in enumerate(tokens) if '+}' in t or '[-' in t ]
    return tokens, [-1] + indices + [len(tokens)]

# 擔心有一句包含兩個 about+} 所以換個邏輯
def divide_triedit_noedit(aft_tokens, indices):
    noedit_list, triedit_list = [], []

    segs = zip(indices, indices[1:])
    for i, (start, end) in enumerate(segs):
        if i != 0 and start > 0 and start+1 < indices[-1]:
            triedit_list.append(tuple(aft_tokens[start-1:start+2]))
        noedit_list.append(aft_tokens[start+1:end])
        
    return noedit_list, triedit_list

def get_bigram(tokens):
    return list(nltk.bigrams(tokens))

def get_trigram(tokens):
    return list(nltk.trigrams(tokens))

### Here
reserved = 'about'

edit_list = [] # trigram edit
bigrams, trigrams = [], []
    
# for line in open('test.txt', 'r', encoding='utf8').readlines():# fileinput.input():
for line in sys.stdin:
    tokens = line.strip().split(' ')

    aft_tokens, indices = to_after(tokens)

    noedit_list, edit_tokens = divide_triedit_noedit(aft_tokens, indices)

    edit_list.extend(edit_tokens)

    # 會有 [] 出現，若是長度不夠
    for no_edit in noedit_list:
        bigrams.extend(get_bigram(no_edit))
        trigrams.extend(get_trigram(no_edit))
        
uniq_edit = set(edit_list)

def bi_vs_edit(bigram, uniq_edit_list):
    group = set()
    for edit in uniq_edit_list:
        if bigram[0] == edit[0] and bigram[1] == edit[2]:
            group.add(edit)
    return group

def tri_vs_edit(trigram, uniq_edit_list):
    group = set()
    for edit in uniq_edit_list:
        if edit[0] == trigram[0] and edit[2] == trigram[2]:
            temp = edit[1][2:-2].split('>>')[0] if edit[1].startswith('[-' + reserved) else edit[1]
            if temp == trigram[1]:
                group.add(edit)
    return group

# not sure if bigrams repeated or not.
count_edit = Counter(edit_list)

count_bi = Counter(bigrams)
for bi in count_bi:
    group = list(bi_vs_edit(bi, uniq_edit))
    if group: 
        line = "%s\t%d\t%s" % (' '.join(bi), count_bi[bi], '\t'.join(["%s|%d" % (' '.join(edit), count_edit[edit]) for edit in group]))
        print(line)

count_tri = Counter(trigrams)
for tri in count_tri:
    group = list(tri_vs_edit(tri, uniq_edit))
    if group: 
        line = "%s\t%d\t%s" % (' '.join(tri), count_tri[tri], '\t'.join(["%s|%d" % (' '.join(edit), count_edit[edit]) for edit in group]))
        print(line)
