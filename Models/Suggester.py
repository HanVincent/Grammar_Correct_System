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

    def process(self, info, k_patterns=5):
        '''{
            'lemma': tk.lemma_,
            'dep': tk.dep_,
            'bef': norm_ptn,
            'ngram': ngram
        }'''
        try:
            pattern_count = self.mongodb_client.get_pattern_counts(
                query={
                    'headword': info['lemma'], 'dependency': info['dep'], 'norm_pattern': info['bef']},
                groupby=None, limit=1).next()['count']
        except StopIteration:
            pattern_count = 0

        top_k_patterns_cursor = self.mongodb_client.get_pattern_counts(
            query={'headword': info['lemma'], 'dependency': info['dep']},
            groupby={"norm_pattern": "$norm_pattern"},
            limit=k_patterns)
        # pattern_candidates = self._suggest_patterns(info['bef'], all_patterns_count_cursor, k=k_patterns)

        try:
            pattern_total_count = self.mongodb_client.get_pattern_counts(
                query={'headword': info['lemma'], 'dependency': info['dep']}).next()['count']
        except StopIteration:
            pattern_total_count = 0

        suggestions = []
        for pattern in top_k_patterns_cursor:
            ngram_tks = info['ngram'].split(' ')
            ngram_candidates = self._suggest_ngrams(
                ngram_tks, pattern['ngrams'])

            percentage = pattern['count'] / pattern_total_count
            if percentage < 0.01:
                continue

            suggestions.append({
                'ptn': pattern['_id']['norm_pattern'],
                'percent': math.floor(percentage*100),
                'ngrams': ngram_candidates
            })
        return suggestions
