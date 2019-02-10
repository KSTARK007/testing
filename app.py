from flask import *
import hashlib
from pymongo import *
import string 

app = Flask(__name__)


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return "bal", 404

@app.route('/')
def index():
	return render_template('form.html',name = "kiran")

client = MongoClient(port=27017)
db=client.cc_assignment.users
cat = client.cc_assignment.categories

def getNextSequence(collection,name):
	collection.update_one( { '_id': name },{ '$inc': {'seq': 1}});
	return int(collection.find_one({'_id':name})["seq"])

#api 1
@app.route('/api/v1/users', methods=['POST'])
def process():
	j = request.get_json()
	name = j['name']
	password = j['password']
	
	if( len(password) != 40 and not all(c in string.hexdigits for c in password) ):
		return jsonify({'code' : 600})

	if name and password:
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
		abort(404)
		return jsonify({'code':404})


#api 3
@app.route('/api/v1/categories', methods=['GET'])
def categorieAdd():
	j = cat.find()
	d = dict()
	for x in j:
		d[x['catName']]=x['size']
	print(d)
	return jsonify(d)


#api 4
@app.route('/api/v1/categories', methods=['POST'])
def categorieList():
	j = request.get_json()
	for k , v in j.items()	:
		result=cat.insert_one({'catId': getNextSequence(client.cc_assignment.orgid_counter,"catId"), 'catName': k, 'size' : v })
	return jsonify({'code':200})


#api 5
@app.route('/api/v1/categories/<categories>', methods=['DELETE'])
def catdelete(categories):
	if(cat.count_documents({"catName":categories})>0):
		cat.delete_one({"catName":categories})
		return jsonify({'code':200})
	else:
		abort(404)
		return jsonify({'code':404})

if __name__ == '__main__':
	app.run(host='0.0.0.0',port=80)