from flask import Flask, jsonify, render_template as render, request, redirect
import requests
import json
from urllib import urlencode
from base64 import urlsafe_b64encode as encode, urlsafe_b64decode as decode
from zlib import compress, decompress

app = Flask(__name__)

@app.route("/")
def home():
    return render("home.html")

@app.route("/request", methods=["POST"])
def make_request():
    url = request.form.get('url', '')
    method = request.form.get('method', '')
    headers = request.form.get('headers', '')
    body = request.form.get('body', '')

    payload = encode(compress(str(
        json.dumps(dict(
            url=url,
            method=method,
            headers=headers,
            body=body
        ))
    )))

    return redirect("/r/%s" % payload)


@app.route("/r/<data>")
def encoded_data(data):
    data = (json.loads(decompress(decode(str(data)))))
    headers = dict(map(lambda x: map(str.strip, str(x).split(':')), filter(None, data['headers'].split('\n'))))

    method = data['method'].lower()
    body = data['body']
    url = data['url']
    if not url.startswith('http'):
        url = 'http://' + url

    resp = methods={
        'get':requests.get,
        'post':requests.post,
        'put':requests.put,
        'delete':requests.delete,
        'head':requests.head,
        'patch':requests.patch
    }[method](url, headers=headers, data=str(body))
    
    return render("response.html", resp=resp, headers=resp.headers, content=resp.text, data=data)

if __name__=='__main__':
    app.run(debug=True)
