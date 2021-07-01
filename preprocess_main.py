
from Models.MongoDBClient import MongoDBClient
from Models.Parser import Parser
from Objects.ParsedEntry import ParsedEntry
from Models.DependencyExtractor import DependencyExtractor
from tqdm import tqdm
from collections import Counter
import gzip
import datetime


class DataCleaner:
    def __init__(self):
        pass

    def is_valid_data(self, parsed_entry, sent):
        if len(parsed_entry) > 24:  # skip long sentence
            return False
        if '@@@' in sent:
            return False
        if '#' in sent:
            return False

        return True


def main():
    parser = Parser()
    data_cleaner = DataCleaner()
    dependency_extractor = DependencyExtractor()
    mongo_client = MongoDBClient()
    mongo_client.create_indexes()
    # filename = 'bnc.parse.txt.gz'
    filename = 'coca.txt.gz'
    with gzip.open('/Users/whan/Data/' + filename, 'rt', encoding='utf8') as fs:
        pattern_counter = Counter()
        ngram_set = set()
        for i, entry in enumerate(tqdm(fs), 1):
            # parsed_entry = ParsedEntry(entry)
            parsed_entry = parser.parse(entry.strip())
            # sent = parsed_entry.origin_sent
            sent = entry 
            if data_cleaner.is_valid_data(parsed_entry, sent):
                sent_score = round(dependency_extractor.score(parsed_entry), 2)
                if sent_score < 0.6:
                    continue

                for token in parsed_entry:
                    info = dependency_extractor.process(token)
                    if info:
                        key = f'{token.lemma_}|{token.dep_}'
                        pattern_counter[(key, info['norm_pattern'])] += 1
                        ngram_key = f'{key}|{info["norm_pattern"]}'
                        ngram = f'{info["ngram"]}|{info["pattern"]}'
                        ngram_set.add((ngram_key, ngram, sent, sent_score))

            if i % 50000 == 0:
                print(i, "Uploading to MongoDB.")

                print("Start to update pattern counts in bulk.")
                start_time = datetime.datetime.now()
                mongo_client.add_patterns(pattern_counter)
                pattern_counter = Counter()
                end_time = datetime.datetime.now()
                print("End update pattern counts in bulk with elapsed seconds: " +
                      str((end_time-start_time).total_seconds()))

                print("Start to insert ngram in bulk.")
                start_time = datetime.datetime.now()
                mongo_client.add_ngrams(ngram_set)
                ngram_set.clear()
                end_time = datetime.datetime.now()
                print("End insert ngram in bulk with elapsed seconds: " +
                      str((end_time-start_time).total_seconds()))

            if i == 20000000:
                break


if __name__ == '__main__':
    main()
