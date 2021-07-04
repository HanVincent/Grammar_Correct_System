from Models.Constant import POS, DEP, WH_WORDS


class PatternExtractor():

    def __init__(self):
        self.pos_type = 'Base'

    def is_processable(self, tag):
        return tag in POS[self.pos_type]

    def _classify_cl(self, token):
        children = list(token.children)
        if children:
            if children[0].tag_ in POS['WH'] or token.lemma_ in WH_WORDS:
                return 'wh-cl'
            if children[0].tag_ == 'TO':
                return 'V'  # to-v
        return 'cl'

    def _map_to_general(self, token):
        tag, dep, lemma = token.tag_, token.dep_, token.lemma_

        # the order matters
        if dep in DEP['CL']:
            return self._classify_cl(token)

        if dep == 'aux' and lemma == 'have':
            return 'have'
        if tag == 'TO':
            return 'to'
        if dep == 'aux':
            return 'aux'
        if lemma == 'be':
            return 'be'
        if tag in POS['WH']:
            return token.text

        if tag == 'VBN':
            return 'V-ed'
        if tag == 'VBG':
            return 'V-ing'
        if tag in POS['VERB']:
            return 'V'

        if token.tag_ in POS['ADJ']:
            return 'adj'
        if token.tag_ in POS['ADV']:
            return 'adv'
        if dep in DEP['PREP']:
            return token.text
        if dep in DEP['SUB']:
            return 'S'
        if dep in DEP['OBJ']:
            return 'O'
        # if token.tag_ in POS['NOUNS']:
        #     return 'n'
        return token.tag_
