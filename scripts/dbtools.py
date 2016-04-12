from pymongo import MongoClient
import random

client = MongoClient("mongodb://localhost")

def rString():
	id_string = ""
	i = 0
	chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
	while i < 8:
		dice = random.randint(0, 1)
		if dice == 0:
			id_string += chars[random.randint(0, (len(chars)-1))
		else:
			id_string += str(random.randint(0, 9))


def submit(title, tags, filters, url, uploader):
	strikes = 0
	if("nsfw" in filters):
		nsfw = True
	else:
		nsfw = False

	if("animated" in filters):
		animated = True
	else:
		animated = False

	db.images.insert({"title":title, "tags":tags, "nsfw":nsfw, "animated":animated, "url":url, "uploader":uploader})
