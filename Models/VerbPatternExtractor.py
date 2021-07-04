from Models.Constant import POS
from Models.PatternExtractor import PatternExtractor


class VerbPatternExtractor(PatternExtractor):

    def __init__(self):
        super(VerbPatternExtractor, self).__init__()
        self.pos_type = 'VERB'

        ####### Dependency pattern #######
        # first layer dependency: dobj, prep, nsubj, nsubjpass, ccomp, xcomp, csubj, csubjpass, prt, acomp, oprd
        # second layer dependency: prep -> pobj, pcomp
        self.FIRST_REMAINS = set(['aux', 'auxpass', 'dobj', 'prep', 'nsubj',
                                 'nsubjpass', 'ccomp', 'xcomp', 'csubj', 'csubjpass', 'prt' 'acomp', 'oprd'])
        self.SECOND_REMAINS = set(['pobj', 'pcomp', 'aux'])
        self.GO_NEXT_WORDS = set(['prep', 'xcomp'])

    def _keep_valid_children(self, tk, deps):
        return [child for child in tk.children if child.dep_ in deps]

    def _flatten(self, list_2d):
        return [el for li in list_2d for el in li]

    def is_processable(self, tag):
        return tag in POS[self.pos_type]

    def extract_pattern(self, head_word):
        first_layer = self._keep_valid_children(head_word, self.FIRST_REMAINS)
        second_layer = self._flatten([self._keep_valid_children(tk, self.SECOND_REMAINS)
                                     for tk in first_layer if tk.dep_ in self.GO_NEXT_WORDS])

        tokens = [head_word] + first_layer + second_layer
        tokens.sort(key=lambda tk: tk.i)

        ngram = [tk.text for tk in tokens]
        indices = set([tk.i for tk in tokens])
        pattern = [self._map_to_general(tk) for tk in tokens]
        if None in pattern or len(pattern) < 2:
            raise ValueError("Invalid pattern:", pattern)

        return (' '.join(pattern), ' '.join(ngram), indices)

    def _stem_pattern(self, pattern, target):
        return target + pattern.split(target, 1)[1]

    # normalize verb pattern
    def normalize(self, pattern, max_length=4):
        if 'be V-ed' in pattern:
            norm_pattern = self._stem_pattern(pattern, 'be V-ed')
        elif 'have V-ed' in pattern:
            norm_pattern = self._stem_pattern(pattern, 'have V-ed')
        elif 'be V-ing' in pattern:
            norm_pattern = self._stem_pattern(pattern, 'be V-ing')
        elif 'be' in pattern:
            norm_pattern = self._stem_pattern(pattern, 'be')
        elif 'V' in pattern:
            norm_pattern = self._stem_pattern(pattern, 'V')
            norm_pattern = norm_pattern.replace(
                'V-ing', 'V').replace('V-ed', 'V')
        else:
            raise ValueError("Pattern not containing 'V' ", pattern)

        # ptn = ptn.replace('wh-cl', 'O').replace('cl', 'O') # cl / wh-cl -> O
        # ptn = ptn.replace('to-v', 'ADJ').replace('v-ing', 'ADJ') # v-ing / to-v -> ?

        # max length
        norm_pattern = norm_pattern.split(' ')[:max_length]

        if len(norm_pattern) == 1:
            return pattern  # return original pattern
        else:
            return ' '.join(norm_pattern)

        # elif len(norm_pattern) > 2:
        #     if pattern[1] in self.PREPOSITIONS:  # V prep. _
        #         pattern = pattern[:3]
        #     elif pattern[1] != 'O':  # V before O
        #         pattern = pattern[:1]
        #     elif pattern[2] in self.PREPOSITIONS:  # V O prep. O
        #         pattern = pattern[:4]
        #     else:  # V O O / V O not_prep
        #         pattern = pattern[:2]
