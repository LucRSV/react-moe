from pymongo import MongoClient
import random
import re

client = MongoClient("mongodb://localhost")
db = client.react

def rString():
	id_string = ""
	i = 0
	chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
	while i < 9:
		dice = random.randint(0, 1)
		if dice == 0:
			id_string += chars[random.randint(0, (len(chars)-1))]
		else:
			id_string += str(random.randint(0, 9))
		i+= 1

	return id_string

def gen_ID():
	taken = True
	while taken == True:
		new_id = rString()
		search = db.images.find({"imgId":new_id})

		if search.count() > 0:
			taken = True
		else:
			return new_id

	return new_id

def validateUrl(url):
	r_url = re.compile(r"^https?:")
	r_image = re.compile(r".*\.(jpe?g|png|gif|svg)$")
	q = db.images.find({"url":url}).count()
	if q > 0:
		return False

	if r_url.match(url):
		if r_image.match(url):
			return True
		else:
			return False
	else:
		return False

def submitImg(title, tags, filters, url, uploader):
	strikes = 0
	if("nsfw" in filters):
		nsfw = True
	else:
		nsfw = False

	if("animated" in filters):
		animated = True
	else:
		animated = False

	validUrl = validateUrl(url)

	imgId = gen_ID()

	if validUrl == True:
		db.images.insert({"title":title, "tags":tags, "nsfw":nsfw, "animated":animated, "url":url, "uploader":uploader, "imgId":imgId})
		for tag in range(len(tags)):
			db.tags.update({"tag":tags[tag]}, {'$inc': {"count": int(1)}}, upsert=True)
		return(imgId)

	elif validUrl == False:
		return('invalid URL supplied')

def getImg(imgId):
	q = db.images.find({'imgId':imgId})
	fields = {}
	for i in q:
		fields["url"] = i["url"]
		fields["tags"] = i["tags"]
		fields["title"] = i["title"]
	return fields

def getImgR(tag, nsfw=False, animated=True):
	search_fields = {}

	search_fields["tags"] = tag
	if nsfw == True:
		search_fields["nsfw"] = True
	elif nsfw == False:
		search_fields["nsfw"] = False

	if animated == False:
		search_fields["animated"] = False

	qCount = db.images.find(search_fields).count()

	try:
		if animated == True:
			rImg = db.images.find({'tags':tag, "nsfw":nsfw})[random.randint(0, qCount-1)]

		elif animated == False:
			rImg = db.images.find({'tags':tag, "nsfw":nsfw, "animated":animated})[random.randint(0, qCount-1)]

		fields = {}
		fields["url"] = rImg["url"]
		fields["tags"] = rImg["tags"]
		fields["title"] = rImg["title"]
		fields["imgId"] = rImg["imgId"]
		return fields

	except:
		return "No image found for tag %s" % (tag)

def getTopTags():
	tags = []
	top = db.tags.find().sort("count", -1).limit(9)
	for tag in top:
		tags.append(tag["tag"])
	return tags
