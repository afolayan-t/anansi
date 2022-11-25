from flask import Flask
import config

app = Flask(__name__)    

@app.route("/")
def sanity_check():
    return "<p>It worked!</p>"

if __name__ == "__main__":
    config.init()
    from crawler import Crawler
    app.run()