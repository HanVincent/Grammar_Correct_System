from Models.DependencyExtractor import DependencyExtractor
from Models.Parser import Parser
from Models.MongoDBClient import MongoDBClient


class Corrector:

    def __init__(self):
        self.CONFIDENT = 0.2
        self.UNCONFIDENT = 0.1

        self.mongodb_client = MongoDBClient()
        self.parser = Parser()
        self.dependency_extractor = DependencyExtractor()

    def _categorize(self, ratio):
        if ratio > self.CONFIDENT:
            return 'right'
        elif ratio < self.UNCONFIDENT:
            return 'wrong'
        else:
            return 'not_sure'

    def _get_template(self, ratio):
        if ratio > self.CONFIDENT:
            return '{{+{}//{}+}}'
        elif ratio < self.UNCONFIDENT:
            return '[-{}//{}-]'
        else:
            return '\\*{}//{}*\\'

    def process(self, sent):
        sent = self.parser.parse(sent)  # TODO: normalize input?

        edits, meta = [], {}
        for token in sent:
            info = self.dependency_extractor.process(token, True)
            if info:
                ratio = self.mongodb_client.get_pattern_ratio(
                    info['headword'], info['dependency'], info['norm_pattern'])
                edits.append(self._get_template(
                    ratio).format(token.text, token.i))
                meta[str(token.i)] = {
                    'lemma': token.lemma_,  # TODO: do we need this?
                    'dep': token.dep_,  # TODO: do we need this?
                    'bef': info['norm_pattern'],  # TODO: or patter? or rename
                    'ngram': info['ngram']
                }
            else:
                edits.append(token.text)

        return (' '.join(edits), meta)
