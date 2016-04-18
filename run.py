from flask import Flask, request, render_template, redirect, url_for
from flask_wtf import Form
from wtforms import TextField, BooleanField, SubmitField
from wtforms.validators import InputRequired
from flaskext.markdown import Markdown
from static.scripts.dbtools import submitImg, getImg, getImgR, getTopTags, db
from flask_recaptcha import ReCaptcha
import random

#Flask configs
application = Flask(__name__)
application.debug = True
application.secret_key = "1121Shoutai"
application.config["RECAPTCHA_SITE_KEY"] = "6LfLVh0TAAAAAA5p4hjpcPcPoAZDtcP3SqG7d7Hv"
application.config["RECAPTCHA_SECRET_KEY"] = "6LfLVh0TAAAAAGlTCKgi_WeuU1D-IOxOnkGO0gGA"
recaptcha = ReCaptcha()
recaptcha.init_app(application)

#Setup Markdown
Markdown(application)

#Submit Image form
class submitForm(Form):
	title = TextField(u'Title')
	url = TextField(u'Image URL', [InputRequired("You must enter an image URL")])
	tags = TextField(u'Tags', [InputRequired("You must enter some tags")])
	nsfw = BooleanField(u'NSFW')
	submit = SubmitField(u'Submit')

@application.route("/")
def main():
#getting our top used tags
	tags_raw = getTopTags()
	tags = {}
	for tag in tags_raw:
		#make sure the tag isn't serving only animated/nsfw images
		if len(tags) > 8:
			break
		try:
			tags[tag] = {"tag":tag, "img":getImgR(tag, False, False)["url"]}
		except:
		#skip if animated or NSFW
			pass
	return render_template('main.html', tags=tags)

@application.route("/add_image", methods=["POST", "GET"])
def addImg():
	form = submitForm()
	if request.method == "GET":
		return render_template('addimg.html', form=form)
	elif request.method == "POST":
		# Adding in image filters for NSFW and animated Gifs
		if recaptcha.verify():
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
					return render_template('addimg.html', form=form, err="Invalid URL supplied or Image has already been submitted.")
				else:
					return redirect(url_for('img', imgId=errCheck))
			else:
				return render_template('addimg.html', form=form, err="An error occured when submitting your image. Please check all fields.")
		else:
			return render_template('addimg.html', form=form, err="Please confirm you're human with the ReCaptcha box.")

@application.route("/about")
def about():
	images = db.images.find().count()
	tags = db.tags.find().count()
	return render_template('about.html', tags=tags, images=images)

@application.route("/img/<imgId>")
#catchall /img/imgId route (ie: react.moe/img/1H9jlKz1)
def img(imgId):
	img = getImg(imgId)
	try:
		return render_template('img.html', img=img["url"], title=img["title"], tags=img["tags"], imgId=imgId)
	except:
		return render_template('img.html', err="Image not found. It may have been removed, or there was a server error.")

@application.route("/remove/<imgId>", methods=["POST", "GET"])
def removeImg(imgId):
	q = db.images.find_one({"imgId":imgId})
	db.claims.insert({"title":q["title"], "imgId":q["imgId"], "uploader":q["uploader"]})
	return render_template("thankyou.html", imgId=imgId)

@application.route("/<tag>")
#catchall for tag. Will add filter parsing later. (IE: react.moe/funny&animated=True)
def rimg(tag):
	animated = True
	nsfw = False
	if len(tag.split("&")) > 1:
		filters = tag.lower().split("&")
		tag = tag.lower().split("&")[0]
		if "animated=false" in filters:
			animated = False
		if "nsfw=true" in filters:
			nsfw = True

	if "%20" in tag:
		newTag = tag.split("%20")
		tag = " ".join(newTag).lower()

	elif "_" in tag:
		newTag = tag.split("_")
		tag = " ".join(newTag).lower()

	img = getImgR(tag, nsfw, animated)
	if img == "No image found for tag %s" % (tag):
		return render_template('img.html', err=img)
	else:
		return render_template('img.html', img=img["url"], title=img["title"], tags=img["tags"], imgId=img["imgId"])

if __name__=="__main__":
	application.run(host="0.0.0.0")
