import sys
from collections import defaultdict
from pprint import pprint

DEP1 = ['root', 'nsubj', 'dobj', 'range', 'attr', 'top', 'nsubjpass']+['prep', 'loc', 'ba', 'cop', 'pass']+['ccomp', 'rcomp', 'conj']
DEP12 = ['prep-pobj', 'prep-pccomp', 'prep-plmod', 'loc-lobj', 'loc-lccomp', 'prep-dep' ]+\
         ['ccomp-nsubj', 'ccomp-dobj', 'ccomp-range', 'ccomp-top', 'ccomp-nsubjpass', 'ccomp-attr', 'rcomp-xsubj', 'ccomp-dep', 'rcomp-dep' ]+\
         ['conj-nsubj', 'conj-dobj', 'conj-range', 'conj-top', 'conj-nsubjpass', 'conj-attr', 'conj-xsubj', 'conj-dep', 'conj-dep' ]
DEP23 = ['plmod-lobj', 'plmod-lccomp', 'lobj-nummod', 'dep-dep']

def sentence_to_relations(sentence):
    dict1 = defaultdict(lambda: 'root')
    for iword, word, tag, dep, ihead in sentence:
        dict1[iword] = dep

    root = [ (iword, word, tag, dep, ihead) for iword, word, tag, dep, ihead in sentence if dep == 'root' ]
    if not root:
        return []
    else:
        root = root[0][0]

    deps1 = [ (iword, word, tag, dep, ihead) for iword, word, tag, dep, ihead in sentence if (ihead == root or dep == 'root') and dep in DEP1 ]
    deps2 = [ (iword, word, tag, dep, ihead) for iword, word, tag, dep, ihead in sentence if dict1[ihead]+'-'+dep in DEP12 \
                         and ihead in [ iword for iword, _, _, _, _ in deps1 ]]
    deps3 = [ (iword, word, tag, dep, ihead) for iword, word, tag, dep, ihead in sentence if dict1[ihead]+'-'+dep in DEP23 \
                         and ihead in [ iword for iword, _, _, _, _ in deps2 ]]
    return sorted( deps1+deps2+deps3, key = lambda x: int(x[0]) )


relatCount = defaultdict(lambda: defaultdict(lambda: 0))
# for 公佈: rela['V:dobj:N']['結果'] = 6276

def countRela(headword, rela, word):
    if headword != '公佈': return
    relatCount[rela][word] += 1
    
def printVAC(relations):    
    wtd, tail, deps = {}, {}, {}
    for iword, word, tag, dep, ihead in relations:
        wtd[iword] = (word, tag, dep)
        tail[ihead] = iword
        deps[(ihead, dep)] = word
    
    for iword, word, tag, dep, ihead in relations:
        if dep in ['nsubj', ]:
            if (ihead, 'dobj') in deps:
                #print ('%s\t%s:%s:%s\t%s' % (word, tag, wtd[ihead][0], 'N', deps[(ihead, 'dobj')]))
                #print ('%s\t%s:subj:%s\t%s' % (wtd[ihead][0], wtd[ihead][1], tag, word))
                countRela(wtd[ihead][0], '%s:subj:%s'%(wtd[ihead][1], 'N'),  word)
            elif (ihead, 'ccomp') in deps:
                #print ('%s\t%s:%s:%s\t%s' % (word, tag, wtd[ihead][0], 'N', deps[(ihead, 'ccomp')]))
                #print ('%s\t%s:subj:%s\t%s' % (wtd[ihead][0], wtd[ihead][1], tag, word))
                countRela(wtd[ihead][0], '%s:subj:%s'%(wtd[ihead][1], 'N'),  word)
            else:
                #print ('%s\t%s:subj:%s\t%s' % (wtd[ihead][0], wtd[ihead][1], tag, word))
                countRela(wtd[ihead][0], '%s:subj:%s'%(wtd[ihead][1], 'N'),  word)
        if dep in ['dobj', 'range']:
            #print ('%s\t%s:obj:%s\t%s' % (wtd[ihead][0], wtd[ihead][1], tag, word))
            countRela(wtd[ihead][0], '%s:obj:%s'%(wtd[ihead][1], 'N'),  word)
        if dep in ['ccomp', 'rcomp', 'xcomp']:
            #print ('%s\t%s:clause:%s\t%s' % (wtd[ihead][0], wtd[ihead][1], tag, word))
            countRela(wtd[ihead][0], '%s:clause:%s'%(wtd[ihead][1], tag),  word)
        if dep == 'prep':

            def getPrepObj(head):
                res = []
                while head in tail:
                    res = [ wtd[tail[head]][0] ] + res
                    head = tail[head]
                return '-'.join(res)
                
            #print ('%s\t%s:%s:%s\t%s' % (wtd[ihead][0], wtd[ihead][1], word, "N", getPrepObj(iword)))
            countRela(wtd[ihead][0], '%s:%s:%s'%(wtd[ihead][1], word, 'N'),  getPrepObj(iword))
    #print ()

def sentences_to_relations(sentences): 
    for sentence in sentences[:]:
        #print ()
        #print (' '.join( [word for _, word, _, _, _ in sentence ]))
        #pprint(sentence)
        #print ()
        relations = sentence_to_relations(sentence)
        printVAC(relations)
    #print top collocations
    relationsColls = []
    for rela in relatCount.keys():
        total = sum( [ x for x in relatCount[rela].values()  ] )
        collCounts = sorted(relatCount[rela].items(), key=lambda x: -x[1])[:10]
        relationsColls += [ (rela, ' '.join([ coll for coll, count in collCounts ]), total) ]
    relationsColls.sort(key=lambda x: -x[2])
    for rela, colls, total in relationsColls[:20]:
        print (rela, colls, total)
    return

def getRootVerb(VERB, infile): 
    sentences = [ block.split('\n')[:] for block in infile.split('\n\n') \
                                if '%s\tV\troot'%VERB in block in block ]
    sentences = [ [ word.strip().split('\t') for word in sentence ] for sentence in sentences ]
    return sentences
    
def grepSentences(sentences, words, N):
    res = sentences
    for word in words:
        res = [ sentence for sentence in res if word in ' '.join( [word for _, word, _, _, _ in sentence ]) ]
    return res[:N]
    
def printSentences(sentences):
    for sentence in sentences:
        for iword, word, tag, dep, ihead in sentence:
            print ('%s\t%s\t%s\t%s\t%s' % (iword, word, tag, dep, ihead))
        print ()
    
if __name__ == '__main__':
    infile = open('gongbu.root.txt', 'r').read()
    sentences = getRootVerb('公佈', infile)
    #sentences = grepSentences(sentences, ['對', '外'], 10)
    #sentences = grepSentences(sentences, ['中壽', '948億'])
    #sentences = grepSentences(sentences, '中壽 日前 公佈 4月 營收 12705 億 元'.split() )
    #sentences = grepSentences(sentences, '友達 已 於 上 周 五 率先 公佈 4月 營收'.split() )
    #printSentences(sentences)
    sentences_to_relations(sentences)
