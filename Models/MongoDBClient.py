import logging
import os
from pymongo import ASCENDING, TEXT, MongoClient


class MongoDBClient:

    def __init__(self):
        username = os.environ['MONGODB_USERNAME']
        password = os.environ['MONGODB_PASSWORD']
        client = MongoClient(
            f"mongodb+srv://{username}:{password}@gec.667g4.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")

        database = client.gec
        self.rule_collection = database.rules  # collection = table

    def create_indexes(self):
        self.rule_collection.create_index([('headword', ASCENDING), ('dependency', ASCENDING), (
            'norm_pattern', ASCENDING), ('pattern', ASCENDING), ('ngram', TEXT)])

    def add_documents(self, documents):
        res = self.rule_collection.insert_many(documents, ordered=False)
        logging.info(res)

    def get_pattern_counts(self, query, groupby=None, count_thres=0, limit=None):
        pipeline = [
            {"$match": query},
            {"$group": {"_id": groupby, "count": {"$sum": 1},
                        "ngrams": {"$addToSet": "$ngram"}}},
            {"$match": {"count": {"$gt": count_thres}}},
            {"$sort": {"count": -1}}
        ]
        if limit:
            pipeline.append({"$limit": limit})

        return self.rule_collection.aggregate(pipeline)

    def get_pattern_ratio(self, headword, dependency, norm_pattern):
        # TODO: refactor by bulk operations
        # pipeline = [
        #     {"$match": query},
        #     {"$group": {"_id": groupby, "count": {"$sum": 1}}},
        #     {"$match": {"count": {"$gt": count_thres}}},
        #     {"$sort": {"count": -1}},
        #     {"$limit": 1}
        # ]
        # self.rule_collection.aggregate(pipeline)

        max_count_cursor = self.get_pattern_counts(
            query={"headword": headword, "dependency": dependency},
            groupby={"norm_pattern": "$norm_pattern"}, limit=1)
        try:
            max_count = max_count_cursor.next()['count']
        except StopIteration:
            return 0

        pattern_count_cursor = self.get_pattern_counts(
            query={"headword": headword, "dependency": dependency,
                   "norm_pattern": norm_pattern},
            groupby=None, limit=1)
        try:
            pattern_count = pattern_count_cursor.next()['count']
        except StopIteration:
            return 0

        return pattern_count / max_count
