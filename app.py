from flask import Flask, render_template, json, request
from flaskext.mysql import MySQL
from mymoodanalyzer import setup, checkin
from requests_oauthlib import OAuth1


app = Flask(__name__)

labels = ['POS', 'NEG', 'OTHER']
colors = ["#32CD32", "#DC143C", "#D3D3D3"]

@app.route('/')
def main():
	return render_template('index.html')

@app.route('/result', methods=['POST'])
def handle_data():
	url = 'https://api.twitter.com/1.1/account/verify_credentials.json'
	auth = OAuth1(your_key, your_api_secret, your_access_token, your_access_token_secret)
	setup(url, auth)
	name = request.form['handle']
	output = checkin(name,auth)
	values = [output["pos_per"], output["neg_per"], 100-output["pos_per"]-output["neg_per"]]
	return render_template('result.html', output=output, set=zip(values, labels, colors))

if __name__ == "__main__":
    app.run()