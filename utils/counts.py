from operator import itemgetter

def get_high_freq(counts):
    values = list(counts.values())
    total, avg, std = np.sum(values), np.mean(values), np.std(values)
    # print("Total: {}, Avg: {}, Std: {}".format(total, avg, std))

    return dict([(ptn, count) for ptn, count in counts.items() if count > avg + std])


def truncate_k(counts, k=10):
    return dict([(ptn, count) for ptn, count in counts.items() if count > k])


def sort_dict(counts):
    if not isinstance(counts, list):
        counts = counts.items()
        
    return sorted(counts, key=itemgetter(1), reverse=True)


Punct = "!?-,:;\"'()"
HiFreWords = open('static/data/HiFreWords.txt', 'r', encoding='utf8').read().split('\t')
Prons = open('static/data/prons.txt', 'r', encoding='utf8').read().split('\n')

def score(sentence):
    tks = sentence.lower().split(' ')
    bad = sum([t not in HiFreWords or t in Prons or t in Punct for t in tks])
    
    return -bad
