from utils.stringUtils import edit_distance
from Models.MongoDBClient import MongoDBClient
import math


class Suggester:
    def __init__(self):
        self.mongodb_client = MongoDBClient()

    def _suggest_patterns(self, original_pattern, all_patterns, k=5):
        original_tokens = original_pattern.split(' ')
        similar_patterns = sorted(all_patterns,
                                  key=lambda pattern: edit_distance(original_tokens,
                                                                    pattern['_id']['norm_pattern'].split(' ')))
        return similar_patterns[:k]

    def _suggest_ngrams(self, ngram_tks, ngram_candidates, k=3):
        similar_ngrams = sorted(
            ngram_candidates, key=lambda ng: edit_distance(ngram_tks, ng.split(' ')))
        return similar_ngrams[:k]

    def _edit_ngram(self):
        pass

    def _edit_sentence(self):
        pass

    def process(self, query, k_patterns=5):
        '''{
            'key': tk.lemma_|tk.dep_,
            'norm_pattern': norm_ptn,
            'ngram': ngram
        }'''
        # pattern_count = self.mongodb_client.get_pattern_count(key, info["bef"])
        total_count = self.mongodb_client.get_total_counts(query['key'])
        top_k_patterns = self.mongodb_client.get_top_pattern_counts(
            query['key'], k_patterns)

        suggestions = []
        ngram_tks = query['ngram'].split(' ')
        for each in top_k_patterns:
            ngram_key = f'{query["key"]}|{each["norm_pattern"]}'
            ngrams = [doc['ngram'].split(
                '|')[0] for doc in self.mongodb_client.get_ngrams(ngram_key)]
            ngram_candidates = self._suggest_ngrams(ngram_tks, ngrams)

            try:
                percentage = each['count'] / total_count
            except ZeroDivisionError:
                percentage = 0

            suggestions.append({
                'norm_pattern': each['norm_pattern'],
                'percent': math.floor(percentage*100),
                'ngrams': ngram_candidates
            })
        return suggestions
