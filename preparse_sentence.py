from Models.Parser import Parser
from utils.stringUtils import normalize
from tqdm import tqdm
import gzip

if __name__ == '__main__':
    parser = Parser()
    with gzip.open('/Users/whan/Data/bnc.parse.txt.gz', 'rt', encoding='utf8') as fs:
        with open('/Users/whan/Data/bnc.parse.new.txt', 'w', encoding='utf8') as ws:
            for i, entry in enumerate(tqdm(fs)):
                for sent in parser.preparse(entry.split('\t')[0]):
                    print(sent, file=ws)
