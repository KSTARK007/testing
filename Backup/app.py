from flask import Flask, render_template, request, jsonify
import hashlib

app = Flask(__name__)

@app.route('/')
def index():
	return render_template('form.html',name = "kiran")

@app.route('/api/v1/users', methods=['POST'])
def process():
	userid = 0
	j = request.get_json()
	name = j['name']
	password = j['password']
	
	fo = open("users.txt","r")
	k = fo.readline()
	while(k != ''):
		userid = k.split(":")[0]
		k = fo.readline()
	fo.close()
	
	if name and password:
		fo = open("users.txt","r")
		k = fo.readline()
		while(k != ''):
			if(name == k.split(":")[1]):
				return jsonify({'code' : 405})
			k = fo.readline()
		fo.close()

		with open("users.txt","a") as fo:
			fo.write(str(int(userid) + 1) + ":" + name + ":" + password + "\n")

		return jsonify({'code' : 201})

	return jsonify({'code' : 400})

if __name__ == '__main__':
	app.run(host='0.0.0.0',port=80,debug=True)