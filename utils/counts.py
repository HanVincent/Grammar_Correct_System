from operator import itemgetter

def edit_distance(s1, s2):
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = range(len(s1) + 1)
    for i2, c2 in enumerate(s2):
        distances_ = [i2+1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    return distances[-1]


def get_high_freq(counts):
    values = list(counts.values())
    total, avg, std = np.sum(values), np.mean(values), np.std(values)
    # print("Total: {}, Avg: {}, Std: {}".format(total, avg, std))

    return dict([(ptn, count) for ptn, count in counts.items() if count > avg + std])


def truncate_k(counts, k=10):
    return { ptn: counts[ptn] for ptn in counts if counts[ptn] > k }


def sort_dict(counts):
    if not isinstance(counts, list):
        return sorted(counts, key=counts.get, reverse=True)
    else:
        return sorted(counts, key=itemgetter(1), reverse=True)


Punct = "!?-,:;\"'()"
HiFreWords = open('static/data/HiFreWords.txt', 'r', encoding='utf8').read().split('\t')
Prons = open('static/data/prons.txt', 'r', encoding='utf8').read().split('\n')

def score(sentence):
    tks = sentence.lower().split(' ')
    bad = sum([t not in HiFreWords or t in Prons or t in Punct for t in tks])
    
    return -bad
