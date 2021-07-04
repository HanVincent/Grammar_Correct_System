from Models.Corrector import Corrector
from Models.Suggester import Suggester
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app)


@app.route('/')
def index():
    return render_template('index.html')


# post /correct data: { content: str }
@app.route('/correct', methods=['POST'])
def correct():
    request_data = request.get_json()
    if not request_data:
        return jsonify({'edit': 'Should not be empty'})

    content = request_data['content']
    print(content)

    edit_line, meta = corrector.process(content)

    return jsonify({'edit': edit_line, 'meta': meta})


# post /suggest data: {'tk': 'want', 'bef': 'V to-v', 'dep': 'ROOT', 'lemma': 'want'}
@app.route('/suggest', methods=['POST'])
def suggest():
    request_data = request.get_json()
    if not request_data:
        return jsonify({'edit': 'Should not be empty'})

    print(request_data)

    return jsonify({'suggests': suggester.process(request_data)})


def init():
    global corrector, suggester

    corrector = Corrector()
    suggester = Suggester()


init()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8889)

    # from pprint import pprint

    # user_input = '''I like you. \n I want discuss exaggerately about my life. I rely my ability.'''
    # user_input = 'can you rely heavily in my life in last July without hestitation?'
    # pprint(corrector.process(user_input))
    # pprint(suggester.process(
        # {'tk': 'rely', 'ngram': 'I rely ability', 'bef': 'V O', 'dep': 'ROOT', 'lemma': 'rely'}))
    # pprint(suggest_info({'tk': 'discuss', 'ngram': 'to discuss about life', 'bef': 'V about O', 'dep': 'xcomp', 'lemma': 'discuss'}))
    # pprint(suggest_info({'bef': 'V to-v', 'dep': 'ROOT', 'ngram': 'I want discuss', 'lemma': 'want'}))
