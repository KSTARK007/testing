from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
	return render_template('form.html')

@app.route('/api/v1/users', methods=['POST'])
def process():
	userid = 0
	name = request.form['name']
	password = request.form['password']
	
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
	app.run(debug=True)