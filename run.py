from flask import Flask, request, render_template
from flaskext.markdown import Markdown
from scripts.dbtools import submit

application = Flask(__name__)

Markdown(application)

@application.route("/")
def main():
	return render_template('main.html')

@application.route("/add_image", methods=["POST", "GET"])
def addImg():
	if request.route == "GET":
		return render_template('addimg.html')
	elif request.route == "POST":
		return render_template('addimg.html')

@application.route("/about")
def about():
	return render_template('about.html')

if __name__=="__main__":
	application.run(host="0.0.0.0")
