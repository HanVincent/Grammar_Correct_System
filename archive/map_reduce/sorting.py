import fileinput
from operator import itemgetter

all_pat = []
for line in fileinput.input():
    patterns = line.split('\t')
    main, total_count = patterns[0].split('|')
    
    total_count = int(total_count)
    if total_count < 5: continue # filter out those low freq patterns
    
    def destruct(el):
        ptn, count = el.split('|')
        count = int(count)
        return [ptn, count, count/total_count]

    # 同組的 pattern 先排序
    items = sorted(map(destruct, patterns[1:]), key=itemgetter(2), reverse=True)

    all_pat.append([[main, total_count]] + items)

# 不同組 pattern 排序
all_pat = sorted(all_pat, key=lambda x: x[1][2], reverse=True) # 抓 index = 2 (ratio)

for pats in all_pat:
    main, total_count = pats[0]
    
    print("{} {}".format(main, total_count))
    for p, count, ratio in pats[1:]:
        print("{}: [{}, {}]".format(p, count, ratio))
    print("="*50)
