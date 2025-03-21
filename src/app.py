from flask import Flask

app = Flask("literature_review_app")

@app.route("/")
def possible_endpoints():
    return "Possible endpoints: /extract_text, /extract_sections"

