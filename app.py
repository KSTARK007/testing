from flask import *
import hashlib
from pymongo import *
import string
import datetime
import re
from flask_cors import *

app = Flask(__name__)
cors = CORS(app)


@app.errorhandler(404)
def page_not_found(e):
    return "error",404

@app.route('/')
@cross_origin()
def index():
	return render_template('form.html')

@app.route('/upload')
def upload():
	return render_template('upload.html')

@app.route('/cat')
def cat():
	return render_template('cat.html')

client = MongoClient(port=27017)
db=client.cc_assignment.users
cat = client.cc_assignment.categories
act = client.cc_assignment.act

def getNextSequence(collection,name):
	collection.update_one( { '_id': name },{ '$inc': {'seq': 1}})
	return int(collection.find_one({'_id':name})["seq"])

#api 1
@app.route('/api/v1/users', methods=['POST'])
def process():
	j = request.get_json()
	name = j['name']
	password = j['password']
	if( len(password) != 40 or not all(c in string.hexdigits for c in password) ):
		return jsonify({'code' : 600})

	if name and password and password != "da39a3ee5e6b4b0d3255bfef95601890afd80709":
		if(db.count_documents({"name":name})>0):
			return jsonify({'code' : 405})

		result=db.insert_one({'userId': getNextSequence(client.cc_assignment.orgid_counter,"userId"), 'name': name, 'password' : password })
		return jsonify({'code' : 201})
	return jsonify({'code' : 400})

#api 2
@app.route('/api/v1/users/<username>', methods=['DELETE'])
def userdelete(username):
	if(db.count_documents({"name":username})>0):
		db.delete_one({"name":username})
		return jsonify({'code':200})
	else:
		return jsonify({'code':404})

#api 3
@app.route('/api/v1/categories', methods=['GET'])
def categorieAdd():
	j = cat.find()
	d = dict()
	for x in j:
		d[x['catName']]=x['size']
	return jsonify(d)

#api 4
@app.route('/api/v1/categories', methods=['POST'])
def categorieList():
	j = re.search("[A-Za-z0-9 _]+",(request.get_data().decode('utf-8')))
	if(j is None):
		return jsonify({'code':400})
	j = j.group(0)
	if(cat.count_documents({"catName":j})>0):
		return jsonify({'code':404})
	result=cat.insert_one({'catId': getNextSequence(client.cc_assignment.orgid_counter,"catId"), 'catName':j , 'size' : 0 })
	return jsonify({'code':200})

#api 5
@app.route('/api/v1/categories/<categories>', methods=['DELETE'])
def catdelete(categories):
	if(cat.count_documents({"catName":categories})>0):
		cat.delete_one({"catName":categories})
		return jsonify({'code':200})
	else:
		return jsonify({'code':404})

#api 6 and 8
@app.route('/api/v1/categories/<categoryName>/acts', methods=['GET'])
def catactsizeprint(categoryName):
	start = request.args.get("start")
	end = request.args.get("end")
	if(start is None and end is None):
		if(not cat.count_documents({"catName":categoryName})>0):
			return jsonify({"code": 400})
		d = dict()
		j = cat.find_one({"catName" : categoryName})
		if(j['size'] < 100):
			l = list()
			if(act.count_documents({"catName":categoryName}) == 0):
				return jsonify({'code':404})
			v = act.find({"catName" : categoryName},{"_id":0})
			for x in v:
				l.append(x)
			return jsonify(l),200
		else:
			return jsonify({"code":413})
	if(start is None or end is None):
		return jsonify({"code":1400})
	else :
		start = int(start)
		end = int(end)
		if(start > end or (start<0 or end <0)):
			return jsonify({"code":1600})
		else :
			diff = end-start
			k = 1
			ll = list()
			val = act.count_documents({"catName":categoryName})
			if(val < diff or diff >100):
				return jsonify({"code" : 1400,"text":"more than 100 values "}),400
			if(val == 0):
				return jsonify({'code':1404})
			v = act.find({"catName" : categoryName},{"_id":0}).sort([("actId",-1)])
			for x in v:
				if(k <= diff):
					ll.append(x)
				k = k + 1
			return jsonify(ll),200

#api 7
@app.route('/api/v1/categories/<categories>/acts/size', methods=['GET'])
def catactsize(categories):
	if(not cat.count_documents({"catName":categories})>0):
		return jsonify({"code": 400})
	else:
		j = cat.find({"catName" : categories})
		for x in j:
			return jsonify(x['size'])

#api 9
@app.route('/api/v1/acts/upvote', methods=['POST'])
def upvote():
	j = request.get_json()
	if(not act.count_documents({"actId":j['actId']})>0):
		return jsonify({"code": 400})
	else:
		act.update_one( { 'actId': j['actId'] },{ '$inc': {'upvote': 1}})
		return jsonify({"code": 200})

#api 10
@app.route('/api/v1/acts/<actId>', methods=['DELETE'])
def actDelete(actId):
	if(not act.count_documents({"actId":int(actId)})>0):
		return jsonify({"code": 400}),400
	else:
		j = act.find({"actId":int(actId)},{"_id":0})
		for i in j:
			l=(i["catName"])
		print(l)
		cat.update_one({ 'catName':l },{ '$inc': {'size': -1}})
		act.delete_one({"actId":int(actId)})
		return jsonify({'code':200})


def validateDateTime(date_text):
    try:
        datetime.datetime.strptime(date_text, '%d-%m-%Y:%S-%M-%H')
        return True
    except ValueError:
        return False
def validateBase64(data_text):
	data_text = data_text.split(",")[1]
	if(re.search("[A-Za-z0-9+/=]", data_text) and len(data_text)%4==0):
		return True
	else:
		return False
#api 11
@app.route('/api/v1/acts', methods=['POST'])
def actUpload():
	j = request.get_json()
	#to validate unique ID
	if(act.count_documents({"actId":j['actId']})>0):
		return jsonify({"code":405})
	#to validate timestamp
	if not validateDateTime(j['timestamp']):
		return jsonify({"code":406})
	#to validate user exists
	if(not db.count_documents({"name":j['username']})>0):
		return jsonify({"code":407})
	#to validate Base64 code
	if(not validateBase64(j['img'])):
		return jsonify({"code":408})
	#to validate upvote
	if("upvote" in j):
		return jsonify({"code":409})
	#to validate that cat exists
	if(not cat.count_documents({"catName":j['categoryName']})>0):
		return jsonify({"code":410})

	result=act.insert_one({'actId':j['actId'] , 'username': j['username'], 'timestamp' : j['timestamp'], 'caption':j['caption'], 'catName':j['categoryName'], 'img':j['img'], 'upvote':0 })
	cat.update_one({ 'catName':j['categoryName'] },{ '$inc': {'size': 1}})
	client.cc_assignment.orgid_counter.update_one( {'_id':"actId"},{'$inc': {'seq': 1}})
	return jsonify({'code':200})

# helper api's
# get act id
@app.route('/api/get/actId')
def actid():
	f = client.cc_assignment.orgid_counter.find_one({"_id":"actId"})
	return jsonify(f['seq'])

#down vote
@app.route('/api/v1/acts/downvote', methods=['POST'])
def downvote():
	j = request.get_json()
	if(not act.count_documents({"actId":j['actId']})>0):
		return jsonify({"code": 400})
	else:
		act.update_one( { 'actId': j['actId'] },{ '$inc': {'upvote': -1}})
		return jsonify({"code": 200})

#login
@app.route('/api/v1/users/login', methods=['POST'])
def processes():
	j = request.get_json()
	name = j['name']
	password = j['password']
	if( len(password) != 40 or not all(c in string.hexdigits for c in password) ):
		return jsonify({'code' : 600 ,"text" :"Sha1 error"})

	if name and password and password != "da39a3ee5e6b4b0d3255bfef95601890afd80709":
		if(db.count_documents({"name":name})<=0):
			return jsonify({'code' : 405 ,"text" :"login fail"})

		v = db.find_one({'name': name},{"_id":0})
		return jsonify({'code' : 201,"text" :"Successfull login","userId":v["userId"]})
	return jsonify({'code' : 400,"text" :"data missing"}),400

#get list of users
@app.route('/api/v1/userlist', methods=['GET'])
def listuser():
	j = db.find()
	d = dict()
	for x in j:
		d[x['name']]=x['userId']
	return jsonify(d)


if __name__ == '__main__':
	app.run(host='0.0.0.0',port=80,debug = True)
