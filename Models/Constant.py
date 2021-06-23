
PUNCTUATIONS = set("!?-,:;\"'()")
COMMON_WORDS = set([word for word in open('data/common_words.txt', 'r', encoding='utf8').read().split('\t')
                    if ' ' not in word])
PRONOUNS = set(['i', 'me', 'you', 'your', 'yours', 'he',
                     'she', 'they', 'him', 'her', 'them', 'his', 'their', 'it'])
PREPOSITIONS = set(['about', 'across', 'against', 'along', 'among', 'around', 'as', 'at',
                    'beside', 'besides', 'between', 'by', 'down', 'during',
                    'except', 'for', 'from', 'in', 'inside', 'into', 'of', 'off',
                    'on', 'onto', 'outside', 'over', 'through', 'to', 'toward', 'towards',
                    'under', 'underneath', 'until', 'up', 'upon', 'with', 'within', 'without'])
# not included: above / behind / beneath /beyond / below ...

WH_WORDS = set(['how', 'who', 'what', 'when', 'why', 'where', 'which', 'whether',
                'whichever', 'whoever', 'whomever', 'whatever', 'wherever', 'whenever'])
RESERVED_WORDS = set(['someway', 'together', 'that'])

POS = {
    'VERB': set(['VB', 'VBD', 'VBG', 'VBP', 'VBZ']),  # 'VBN'
    'NOUN': set(['NN', 'NNP', 'NNS', 'NNPS', 'DT', 'PRP', 'CD']),
    'ADJ':  set(['JJ', 'JJR', 'JJS']),
    'ADV':  set(['RB', 'RBR', 'RBS']),
    'PREP': set(['IN']),
    'WH':   set(['WDT', 'WP', 'WP$', 'WRB'])
}

DEP = {
    'SUB':  set(['nsubj', 'nsubjpass', 'oprd']),
    'OBJ':  set(['dobj', 'pobj']),
    'CL':   set(['ccomp', 'xcomp', 'acomp', 'pcomp', 'csubj', 'csubjpass']),
    'PREP': set(['prep', 'prt'])
}
