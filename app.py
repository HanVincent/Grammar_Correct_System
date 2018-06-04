#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask

app = Flask(__name__)

# @app.route("/<query>")
# def correct(query):
#     pass

# post / data: {content :}
@app.route('/' , methods=['POST'])
def correct():
    request_data = request.get_json()
    content = request_data['content']
    
    return jsonify(content)

if __name__ == "__main__":
    app.run()
