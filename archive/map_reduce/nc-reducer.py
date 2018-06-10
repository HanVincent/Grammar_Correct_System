import fileinput
from collections import Counter, defaultdict
from itertools import groupby
from operator import itemgetter

groups = defaultdict(Counter)

def parse_line(line):
    head, count, ngrams = line.strip().split('\t', maxsplit=2)
    ngrams = ngrams.split('\t')
    return head, int(count), ngrams

# fileinput v.s. stdin
records = map(parse_line, fileinput.input())
for head, records in groupby(records, key=itemgetter(0)):
    edit_dict, total_count = Counter(), 0
    for _, count, ngrams in records:
        total_count += count
        for ngram in ngrams:
            edit, cnt = ngram.split('|')
            edit_dict[edit] += int(cnt)
    
    temp = '\t'.join([ "{}|{}".format(edit, count) for edit, count in edit_dict.items() ])
    print("{}|{}\t{}".format(head, total_count, temp))
    