PREPOSITIONS = ['about', 'across', 'against', 'along', 'among', 'around', 'as', 'at',
                'beside', 'besides', 'between', 'by', 'down', 'during', 
                'except', 'for', 'from', 'in', 'inside', 'into', 'of', 'off', 
                'on', 'onto', 'outside', 'over', 'through', 'to', 'toward', 'towards', 
                'under', 'underneath', 'until', 'up', 'upon', 'with', 'within', 'without']
# not inlcuded: above / behind / beneath /beyond / below ... 

WH_WORDS = ['how', 'who', 'what', 'when', 'why', 'where', 'which', 'whether', 'whichever', 'whoever', 'whomever', 'whatever', 'wherever', 'whenever']
RESERVED_WORDS = ['someway, together', 'that']

POS = {
    'VERBS': ['VB', 'VBD', 'VBG', 'VBP', 'VBZ'], # 'VBN'
    'NOUNS': ['NN', 'NNP', 'NNS', 'NNPS', 'DT', 'PRP', 'CD'],
    'ADJ':   ['JJ', 'JJR', 'JJS'],
    'ADV':   ['RB', 'RBR', 'RBS'],
    'PREP':  ['IN'],
    'WH':    ['WDT', 'WP', 'WP$', 'WRB']
}

DEP = {
    'SUB':  ['nsubj', 'nsubjpass', 'oprd'],
    'OBJ':  ['dobj', 'pobj'],
    'CL':   ['ccomp', 'xcomp', 'acomp', 'pcomp', 'csubj', 'csubjpass'],
    'PREP': ['prep', 'prt']
}



def is_past_passive(main_verb):
    if main_verb.tag_ != 'VBN':
        return False
    
    return any([child.lemma_ == 'be' for child in main_verb.children])


def is_noun_chunk(cur_token):
    for nc in cur_token.doc.noun_chunks:
        if cur_token.i in range(nc.start, nc.end):
            return True, nc.end
        
    return False, cur_token.i + 1


####### Dependency pattern #######
# 第一層 dependency: dobj, prep, nsubj, nsubjpass, ccomp, xcomp, csubj, csubjpass, prt, acomp, oprd
# 第二層 dependency: prep -> pobj, pcomp


def classify_cl(token):
    children = list(token.children)
    if children:
        if children[0].tag_ in POS['WH']: return 'wh-cl'
        if children[0].tag_ == 'TO':      return 'to-v'
    return 'cl'
    
    
def head_mapping(token):
    if token.tag_ == 'VBN':         return 'V-ed'
    if token.tag_ == 'VBG':         return 'V-ing'
    if token.tag_ in POS['VERBS']:  return 'V'
    
    return None
    
    
def dep_mapping(token):
    # 順序 matters
    if token.dep_ in DEP['CL']:         return classify_cl(token)    
    
    if token.dep_   == 'aux' and token.lemma_ == 'have': return 'have'
    if token.lemma_ == 'be':     return 'be'
    
    if token.tag_ == 'VBN':             return 'v-ed'
    if token.tag_ == 'VBG':             return 'v-ing'
    if token.tag_ in POS['VERBS']:      return 'v'

    if token.dep_ in DEP['SUB']:        return 'S'
    if token.dep_ in DEP['OBJ']:        return 'O'
    if token.dep_ in DEP['PREP']:       return token.text
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


def dep_to_ptns_ngrams(head_word):
    first_layer  = keep_children(head_word, FIRST_REMAINS)
    second_layer = flattern([keep_children(tk, SECOND_REMAINS) for tk in first_layer if tk.dep_ in go_deeper])
    
    tokens = [head_word] + first_layer + second_layer
    tokens.sort(key=lambda tk: tk.i)

    ptns = [head_mapping(tk) if tk.i == head_word.i else dep_mapping(tk) for tk in tokens]
    
    # ptn = ' '.join([p for p in ptns if p]) # Avoid None
    # ngram = ' '.join([tk.text for tk in tokens])
    
    ptns = [p for p in ptns if p]
    ngrams = [tk for tk in tokens]

    return ptns, ngrams



####### N-gram pattern #######

def pos_mapping(token):
    if token.text in RESEVERED_WORDS: return token.text
    if token.lemma_ == 'be':          return 'be'
    
    if token.tag_ in POS['NOUNS']:    return 'n'
    if token.tag_ in POS['PREP']:     return token.text

    if token.tag_ in POS['ADJ']:      return 'adj'
    if token.tag_ in POS['ADV']:      return 'adv'
    
    if token.tag_ == 'VBG':           return 'v-ing'
    if token.tag_ == 'VBN':           return 'v-ed'
    if token.tag_ in POS['VERBS']:    return 'v'
    
    if token.tag_ in POS['WH'] and token.lemma_ in WH_WORDS: return 'wh' # 多加 why, which, where
    
    return token.tag_
