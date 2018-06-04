def to_after_token(token):
    token = token.replace('\u3000', ' ')
    if token == ' ': return ''

    if token.endswith('-]'):
        return None
    elif token.endswith('+}'):
        return token[token.rfind('>>')+2:-2]  if token.startswith('[-') else token[2:-2]
    else:
        return token
        
def to_after(tokens):
    tokens = [e for token in map(to_after_token, tokens) if token for e in token.split(' ')]
    return tokens

def to_before_token(token):
    token = token.replace('\u3000', ' ')
    if token == ' ': return ''

    if token.endswith('-]'):
        return token[2:-2]
    elif token.endswith('+}'):
        return token[2:token.rfind('>>')]  if token.startswith('[-') else None
    else:
        return token
        
def to_before(tokens):
    return [ token for token in map(to_before_token, tokens) if token ]


if __name__ == '__main__':
    loc = '../dataset/efcamp/'
    fs = open(loc + 'ef.sent.wrong.right.txt', 'w', encoding='utf8')
    for line in open(loc + 'ef.diff.simplize.despace.txt', 'r', encoding='utf8'):
        tokens = line.strip().split(' ')
        aft_tokens = to_after(tokens)
        bef_tokens = to_before(tokens)
        print("{}\t{}\t{}".format(' '.join(tokens), ' '.join(aft_tokens), ' '.join(bef_tokens)), file=fs)

    fs.close()

