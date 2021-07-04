from Models.VerbPatternExtractor import VerbPatternExtractor
from Models.Parser import Parser


def main():
    parser = Parser()
    parsed_entry = parser.parse('Where I want to be.')
    verb_pattern_extractor = VerbPatternExtractor()

    pattern, ngram, indices = verb_pattern_extractor.extract_pattern(
        parsed_entry[2])

    print(pattern)
    print(verb_pattern_extractor.normalize(pattern))


if __name__ == '__main__':
    main()
