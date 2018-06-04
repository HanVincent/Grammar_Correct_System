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
    # temp 
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
