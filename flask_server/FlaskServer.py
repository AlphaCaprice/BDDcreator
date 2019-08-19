from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from graphviz import render
import pprint


from flask_server import diagram_functions


app = Flask(__name__)
CORS(app)


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/FlaskServer/", methods=['POST', 'GET'])
def _get_data():
    data = request.get_json()
    pprint.pprint(data)
    formula_text = (diagram_functions.latex2text(data.get("formula")))
    file_path_self_generated = diagram_functions.text2bddExpr(formula_text)
    file_path_getted = diagram_functions.get_dot_from_json(data, "json_from_server")
    render("dot", "png", file_path_getted)
    # print(file_path_self_generated)
    # print(file_path_getted)
    answer = diagram_functions.dot_files_comparator(file_path_getted, file_path_self_generated)
    print(answer)
    respond = jsonify(answer=answer)
    return respond


if __name__ == "__main__":
    app.run(host='0.0.0.0')
