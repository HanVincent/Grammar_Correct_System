def get_high_freq(counts):
    values = list(counts.values())
    total, avg, std = np.sum(values), np.mean(values), np.std(values)
    # print("Total: {}, Avg: {}, Std: {}".format(total, avg, std))

    return dict([(ptn, count) for ptn, count in counts.items() if count > avg + std])


def truncate_k(counts, k=10):
    return dict([(ptn, count) for ptn, count in counts.items() if count > k])


def sort_dict(counts):
    return sorted(counts.items(), key=itemgetter(1), reverse=True)