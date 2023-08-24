import os

from dotenv import load_dotenv

from utilities.llm_helper import LLMHelper

load_dotenv()

from flask import Flask, jsonify, request
from gevent import pywsgi

# Flask 初始化
app = Flask(__name__)


# 定义 RESTful API 路由
@app.route("/api/answer", methods=["GET"])
def api_answer():
    question = request.args.get("question")
    llm_helper = LLMHelper()
    question, response, context, sources = llm_helper.get_semantic_answer(question, [])
    return jsonify({
        "response": response,
        "sources": sources
    })


class Api:
    def __init__(self):
        self.server = None
        self.api_port = int(os.getenv("API_PORT", "8080"))

    def start_server(self):
        self.server = pywsgi.WSGIServer(('0.0.0.0', self.api_port), app)
        self.server.serve_forever()

    def stop_server(self):
        self.server.stop()

