def is_past_passive(main_verb):
    if main_verb.tag_ != 'VBN':
        return False
    return any([child.lemma_ == 'be' for child in main_verb.children])


def is_noun_chunk(cur_token):
    for nc in cur_token.doc.noun_chunks:
        if cur_token.i in range(nc.start, nc.end):
            return True, nc.end
    return False, cur_token.i + 1

####### N-gram pattern #######

VERBS = ['VB', 'VBD', 'VBG', 'VBP', 'VBZ']
NOUNS = ['NN', 'NNP', 'NNS', 'NNPS', 'DT', 'PRP', 'CD']
ADJ   = ['JJ', 'JJR', 'JJS']
ADV   = ['RB', 'RBR', 'RBS']
PREP  = ['IN']
WH    = ['WDT', 'WP', 'WP$', 'WRB']
wh_word = ['how', 'who', 'what', 'when', 'why', 'where', 'which', 'whether', 'whichever', 'whoever', 'whomever', 'whatever', 'wherever', 'whenever']
reserved_words = ['someway, together', 'that']

def pos_mapping(token):
    # temp -> head_mapping
    if token.lemma_ == TARGET_WORD:  
        if token.tag_ == 'VBN':      return 'VBN'
        if token.tag_ in VERBS:      return 'V'

    if token.text in reserved_words: return token.text
    if token.lemma_ == 'be':         return 'be'
    
    if token.tag_ in NOUNS:          return 'n'
    if token.tag_ in PREP:           return token.text

    if token.tag_ in ADJ:            return 'adj'
    if token.tag_ in ADV:            return 'adv'
    
    if token.tag_ == 'VBG':          return 'v-ing'
    if token.tag_ == 'VBN':          return 'v-ed'
    if token.tag_ in VERBS:          return 'v'
    
    if token.tag_ in WH and token.lemma_ in wh_word: return 'wh' # 多加 why, which, where
    
    return token.tag_


####### Dependency pattern #######
# 第一層 dependency: dobj, prep, nsubj, nsubjpass, ccomp, xcomp, csubj, csubjpass, prt, acomp, oprd
# 第二層 dependency: prep -> pobj, pcomp

SUB  = ['nsubj', 'nsubjpass', 'oprd']
OBJ  = ['dobj', 'pobj']
CL   = ['ccomp', 'xcomp', 'acomp', 'pcomp', 'csubj', 'csubjpass']
PREP = ['prep', 'prt']

def classify_cl(token):
    children = list(token.children)
    if children:
        if children[0].tag_ in WH: return 'wh-cl'
        if children[0].tag_ == 'TO': return 'to-v'
    return 'cl'
    
def head_mapping(token):
    if token.tag_ == 'VBN':      return 'V-ed'
    if token.tag_ == 'VBG':      return 'V-ing'
    if token.tag_ in VERBS:      return 'V'
    return None
    
def dep_mapping(token):
    # 順序 matters
    if token.dep_ in CL:         return classify_cl(token)    
    
    if token.dep_ == 'aux' and token.lemma_ == 'have': return 'have'
    if token.lemma_ == 'be':     return 'be'
    
    if token.dep_ in SUB:        return 'S'
    
    if token.tag_ == 'VBN':      return 'v-ed'
    if token.tag_ == 'VBG':      return 'v-ing'
    if token.tag_ in VERBS:      return 'v'
    
    if token.dep_ in OBJ:        return 'O'
    if token.dep_ in PREP:       return token.text
    if token.tag_ == 'TO':       return 'to'
    
    return None


####### Retrieve Dep pattern #######
FIRST_REMAINS = ['aux', 'auxpass', 'dobj', 'prep', 'nsubj', 'nsubjpass', 'ccomp', 'xcomp', 'csubj', 'csubjpass', 'prt' 'acomp', 'oprd']
SECOND_REMAINS = ['pobj', 'pcomp']
go_deeper = ['prep']

def keep_children(tk, rules):
    return [child for child in tk.children if child.dep_ in rules]

def flattern(list_2d):
    return [el for li in list_2d for el in li]

def dep_to_pattern(head_word):
    first_order  = keep_children(head_word, FIRST_REMAINS)
    second_order = flattern([keep_children(tk, SECOND_REMAINS) for tk in first_order if tk.dep_ in go_deeper])
    
    tokens = [head_word] + first_order + second_order
    tokens.sort(key=lambda tk: tk.i)

    ptns = [head_mapping(tk) if tk.i == head_word.i else dep_mapping(tk) for tk in tokens]
    
    ptn = ' '.join([p for p in ptns if p])
    ngram = ' '.join([tk.text for tk in tokens])

    return ptn, ngram