from flask import Flask,render_template, jsonify, redirect, url_for, request,session,Response
from snapshot import takePhoto, deletePhoto ## Bryan
from functools import wraps 
import string
import random
import sys
import logging
import os
import boto3
import time
from boto3.dynamodb.conditions import Key, Attr
import dynamodb
import jsonconverter as jsonc
from camera_pi import Camera

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)



# generate random session key
def rng_generator(size=6, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))
app.secret_key = rng_generator()

#Prevent force browsing
def login_required(f):
	@wraps(f)
	def wrap(*args, **kwargs):
	    if 'logged_in' in session:
	        return f(*args, **kwargs)
	    else:
	        return redirect(url_for('login'))
	return wrap

#Login
@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	try:
		dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
		table = dynamodb.Table('ush_login')
		response = table.scan()
		items = response['Items']

		if request.method == 'POST':
			for i in items:
				if request.form['password'] == i['password'] and request.form['username'] == i['username']:
					session['logged_in'] = True
					return redirect(url_for('homepage'))
				else:
					error = 'wrong username or password'
					return redirect(url_for('login'),error=error)

	except Exception as e: 
		print(e) 
	return render_template('login.html', error=error)

# Logout
@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))





@app.route('/changepassword',methods=['GET','POST'])
@login_required
def changepw():
	try:
		formpassword = request.form['password']
		dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
		table = dynamodb.Table('ush_login')

		table.update_item(
 Key={
        'username': 'admin'
    },
    UpdateExpression='SET password = :val1',
    ExpressionAttributeValues={

        ':val1': formpassword
    }
)

		session.pop('logged_in',None)
		return redirect(url_for('login'))
	except Exception as e: 
		print(e)

	return render_template('changepassword.html')








@app.route('/settings')
@login_required
def settings():
	return render_template('settings.html')



@app.route('/garage')
@login_required
def garage():
	data = []
	dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
	table = dynamodb.Table('ush_carplate')
	response = table.scan()
	items = response['Items']
	for i in response['Items']:
		data.append(tuple(i.values()))

	return render_template('garage.html',data=data)


#live camera stream for garage
def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
@login_required
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/lisenceplate')
@login_required
def lisenceplate():
	data = []
	dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
	table = dynamodb.Table('ush_authorise_carplate')
	response = table.scan()
	items = response['Items']
	for i in response['Items']:
		data.append(tuple(i.values()))

	return render_template('lisenceplate.html',data=data)


#insert, update and update authorisation lp table
@app.route('/lisenceplate', methods=['GET', 'POST'])
@login_required
def insertupdatelp():
	dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
	table = dynamodb.Table('ush_authorise_carplate')


	formcurrentlisenceplate = request.form['currentLP']
	formlisenceplate = request.form['insertLP']
	formdeletelisenceplate = request.form['deleteLP']

	if formdeletelisenceplate != "null":
		table.delete_item(
		Key={

				'carplate': formdeletelisenceplate
		},

		)


	if formcurrentlisenceplate != "null":
		table.delete_item(
		Key={

				'carplate': formcurrentlisenceplate
		},

		)


	if formlisenceplate != "null" or formcurrentlisenceplate != "null":
		table.update_item(
	    Key={
	        'carplate': formlisenceplate
	    },
	   UpdateExpression='SET authorisedate = :val1',
	    ExpressionAttributeValues={
	        ':val1': time.strftime("%d-%b-%Y %H:%M:%S")
	    }
		)


	return redirect(url_for('lisenceplate'))






@app.route("/homepage")
@login_required
def homepage():
	return render_template("homepage.html")

@app.route('/homepage', methods=['POST','GET'])
@login_required
def index():
    if request.method == 'POST' or request.method == 'GET':
        try:
            data = {'chart_data': jsonc.data_to_json(dynamodb.get_data_from_dynamodb()), 
             'title': "IOT Data"}
            print data
            return jsonify(data)
        except:
            import sys
            print 'error'
            print(sys.exc_info()[0])
            print(sys.exc_info()[1])


@app.route('/changeKeypad')
@login_required
def keypadpassword():
    return render_template('changekeypad.html')

@app.route("/changeKeypad",methods=['GET','POST'])
@login_required
def modifyKeypad():
    keypadpassword = request.form['password']
    try:
        ## Update Database
        import boto3

        #dynamodb = boto3.resource('dynamodb')
        dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
        table = dynamodb.Table('ush_pin')

        table.update_item(
            Key={
            'deviceid': 'deviceid_bryantay'
            },
            UpdateExpression='SET pin = :val1',
            ExpressionAttributeValues={
            ':val1': keypadpassword
            }
            )
        return(redirect(url_for('settings')))

    except Exception as e: 
        print(e)


@app.route('/changeThreshold')
@login_required
def Threshold():
    return render_template('changethreshold.html')

@app.route("/changeThreshold",methods=['GET','POST'])
@login_required
def modifyThreshold():
    threshold = request.form['password']
    try:
        ## Update Database
        import boto3

        #dynamodb = boto3.resource('dynamodb')
        dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
        table = dynamodb.Table('ush_pin')

        table.update_item(
            Key={
            'deviceid': 'deviceid_bryantay'
            },
            UpdateExpression='SET threshhold = :val1',
            ExpressionAttributeValues={
            ':val1': threshold
            }
            )
        return(redirect(url_for('settings')))

    except Exception as e: 
        print(e)

@app.route('/registerFace')
@login_required
def registerFace():
    return render_template('registerFace.html')

@app.route("/registerFace",methods=['GET','POST'])
@login_required
def registeringFace():

    userName = request.form['username']

    takePhoto(userName)

    return(redirect(url_for('settings')))

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0',threaded=True)