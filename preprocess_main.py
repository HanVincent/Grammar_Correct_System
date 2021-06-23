
from Models.MongoDBClient import MongoDBClient
from Objects.ParsedEntry import ParsedEntry
from Models.DependencyExtractor import DependencyExtractor
from tqdm import tqdm
import gzip


class DataCleaner:
    def __init__(self):
        pass

    def is_valid_data(self, parsed_entry):
        if len(parsed_entry) > 24:  # skip long sentence
            return False
        if '@@@' in parsed_entry.original_sent:
            return False
        if '#' in parsed_entry.original_sent:
            return False

        return True


def main():
    data_cleaner = DataCleaner()
    dependency_extractor = DependencyExtractor()
    mongo_client = MongoDBClient()
    mongo_client.create_indexes()

    with gzip.open('/Users/whan/Data/bnc.parse.txt.gz', 'rt', encoding='utf8') as fs:
        documents = []
        for i, entry in enumerate(tqdm(fs), 1):
            parsed_entry = ParsedEntry(entry)
            if data_cleaner.is_valid_data(parsed_entry):
                sent_score = dependency_extractor.score(parsed_entry)
                if sent_score < 0.6:
                    continue

                patterns = map(
                    lambda token: dependency_extractor.process(token), parsed_entry)
                patterns = filter(lambda pattern: pattern,
                                  patterns)  # filter None
                for pattern in patterns:
                    pattern['sent'] = parsed_entry.original_sent
                    pattern['sent_score'] = sent_score

                documents.extend(patterns)

            if i % 20000 == 0:
                mongo_client.add_documents(documents)
                documents = []

            if i == 5000000:
                break


if __name__ == '__main__':
    main()
