import logging
import os
from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.operations import UpdateOne


class MongoDBClient:

    def __init__(self):
        username = os.environ['MONGODB_USERNAME']
        password = os.environ['MONGODB_PASSWORD']
        client = MongoClient(
            f"mongodb+srv://{username}:{password}@gec.667g4.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")

        database = client.gec
        self.pattern_collection = database.patterns  # collection = table
        self.ngram_collection = database.ngrams

    def create_indexes(self):
        self.pattern_collection.create_index(
            [('key', ASCENDING), ('norm_pattern', ASCENDING)])
        self.ngram_collection.create_index(
            [('key', ASCENDING), ('ngram', ASCENDING)])

    def add_patterns(self, pattern_counter):
        operations = [
            UpdateOne({'key': key, 'norm_pattern': norm_pattern},
                      {'$set': {
                          'key': key,
                          'norm_pattern': norm_pattern
                      }, '$inc': {'count': count}},
                      upsert=True) for (key, norm_pattern), count in pattern_counter.items()
        ]
        res = self.pattern_collection.bulk_write(operations, ordered=False)
        logging.info(res)

    def add_ngrams(self, ngram_set):
        operations = [
            UpdateOne({'key': key, 'ngram': ngram},
                      {'$set': {
                          'key': key,
                          'ngram': ngram,
                          'sent': sent,
                          'sent_score': score
                      }},
                      upsert=True) for (key, ngram, sent, score) in ngram_set
        ]
        res = self.ngram_collection.bulk_write(operations, ordered=False)
        logging.info(res)

    def get_top_pattern_counts(self, key, top_k=1):
        return self.pattern_collection.find({'key': key}).sort('count', DESCENDING).limit(top_k)

    def get_total_counts(self, key):
        pipeline = [
            {'$match': {'key': key}},
            {'$group': {'_id': '$key', 'count': {'$sum': '$count'}}}
        ]
        try:
            return self.pattern_collection.aggregate(pipeline).next()['count']
        except StopIteration:
            return 0

    def get_pattern_count(self, key, norm_pattern):
        try:
            return self.pattern_collection.find(
                {'key': key, 'norm_pattern': norm_pattern}).limit(1).next()['count']
        except StopIteration:
            return 0

    def get_pattern_ratio(self, key, norm_pattern):
        try:
            max_count = self.get_top_pattern_counts(
                key, top_k=1).next()['count']
        except StopIteration:
            return 0

        pattern_count = self.get_pattern_count(key, norm_pattern)
        return pattern_count / max_count

    def get_ngrams(self, key):
        return self.ngram_collection.find({'key': key})
