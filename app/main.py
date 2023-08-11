import json
from flask import request, Flask, render_template
from app.report import printReport

app = Flask(__name__)

@app.route('/')
def main():
	return render_template("index.html")

@app.route('/api/v1/report', methods = ['POST'])
def api():
	if request.method == 'POST':
		file = request.files['file']

		result = printReport(file)

		return app.response_class(
			response=json.dumps(result, indent=4, ensure_ascii=False),
			status=200,
			mimetype='application/json'
		)
