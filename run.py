from flask import Flask, request, render_template, redirect, url_for
from flask_wtf import Form
from wtforms import TextField, BooleanField, SubmitField
from wtforms.validators import InputRequired
from flaskext.markdown import Markdown
from static.scripts.dbtools import submitImg, getImg, getImgR, getTopTags
import random

application = Flask(__name__)
application.debug = True
application.secret_key = "1121Shoutai"

Markdown(application)

class submitForm(Form):
	title = TextField(u'Title')
	url = TextField(u'Image URL', [InputRequired("You must enter an image URL")])
	tags = TextField(u'Tags', [InputRequired("You must enter some tags")])
	nsfw = BooleanField(u'NSFW')
	submit = SubmitField(u'Submit')

@application.route("/")
def main():
	tags_raw = getTopTags()
	tags = {}
	for t in range(len(tags_raw)):
		tags[tags_raw[t]] = {"tag":tags_raw[t], "img":getImgR(tags_raw[t])["url"]}

	return render_template('main.html', tags=tag)

@application.route("/add_image", methods=["POST", "GET"])
def addImg():
	form = submitForm()
	if request.method == "GET":
		return render_template('addimg.html', form=form)
	elif request.method == "POST":
		# Adding in image filters for NSFW and animated Gifs
		if form.validate():
			filters = []
			if form.nsfw.data == True:
				filters.append("nsfw")
			if ".gif" in form.url.data:
				filters.append("animated")

			tags = form.tags.data.split(",")
			for i in range(len(tags)):
				tags[i] = tags[i].lower()
				if tags[i][0] == " ":
					tags[i] = tags[i][1:]

			uploader = []
			uploader.append(request.environ.get('HTTP_X_REAL_IP', request.remote_addr))
			errCheck = submitImg(form.title.data, tags, filters, form.url.data, uploader)
			if errCheck == 'invalid URL supplied':
				err = errCheck
				return render_template('addimg.html', form=form, err=err)
			else:
				return redirect(url_for('img', imgId=errCheck))
		else:
			return render_template('addimg.html', form=form, err="An error occured when submitting your image. Please check all fields.")

@application.route("/about")
def about():
	return render_template('about.html')

@application.route("/img/<imgId>")
def img(imgId):
	img = getImg(imgId)
	try:
		return render_template('img.html', img=img["url"], title=img["title"], tags=img["tags"], imgId=imgId)
	except:
		return render_template('img.html', err="Image not found. It may have been removed, or there was a server error.")

@application.route("/<tag>")
def rimg(tag):
	if "%20" in tag:
		newTag = tag.split("%20")
		tag = " ".join(newTag).lower()

	elif "_" in tag:
		newTag = tag.split("_")
		tag = " ".join(newTag).lower()

	img = getImgR(tag)
	if img == "No image found for tag %s" % (tag):
		return render_template('img.html', err=img)
	else:
		return render_template('img.html', img=img["url"], title=img["title"], tags=img["tags"], imgId=img["imgId"])

if __name__=="__main__":
	application.run(host="0.0.0.0")
