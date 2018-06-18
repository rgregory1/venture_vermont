from flask import Flask, flash, make_response, render_template, request, redirect, escape, jsonify, Response, url_for, session
from flask_uploads import UploadSet, configure_uploads, IMAGES
import json
import os
import datetime
import pathlib
from functions import *
from werkzeug.utils import secure_filename
import pprint
from PIL import Image
from functools import wraps
from credentials import login_creds

ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'heic'])

app = Flask(__name__)
app.secret_key = 'my_secret_key'

basedir = pathlib.Path.cwd()
# alt base directory to try
# basedir = pathlib.Path(__file__).parent.resolve()

def cookie_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'family' not in request.cookies:
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
	if 'family' in request.cookies:
		return redirect(url_for('activity_picker'))
	else:
		return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		username = request.form['username']
		print(username)
		password = request.form['password']
		print(password)
		for user in login_creds:
			print(login_creds[user]['username'])
			try:
				if login_creds[user]['username'] == username:
					print('passwords: ' + login_creds[user]['password'] + password)
					if login_creds[user]['password'] == password:
						print('everything matches')
						alert_box_class = 'happy'
						results = 'You are logged in.'
						resp = make_response(render_template('login_form.html', alert_box_class=alert_box_class, results=results))
						print('created response')
						resp.set_cookie('family', login_creds[user]['family_cookie'])
						print('createde cookie')

						#return render_template('login_form.html', alert_box_class=alert_box_class, results=results)
						# return render_template('login_form.html', alert_box_class=alert_box_class, results=results, resp=resp)
						return resp
			except:
				print('now in exception')
				alert_box_class = 'alert'
				results = 'This info does not match our records.'
				return render_template('login_form.html', alert_box_class=alert_box_class, results=results)
	# alert_box_class = 'username did not work'
	# results = 'make it work'
	return render_template('login_form.html')

@app.route('/logout')
def logout():
	resp = make_response(render_template('login_form.html'))
	resp.delete_cookie('family')
	return resp

@app.route('/activity_picker')
@cookie_required
def activity_picker():
	family = request.cookies.get('family')
	data = grab_from_storage(family, basedir)
	return render_template('activity_picker.html', data=data)


@app.route('/apply_activity', methods=['POST'])
@cookie_required
def apply_activity():
	family = request.cookies.get('family')
	data = grab_from_storage(family, basedir)
	activity_selected = request.form['activity_selected']
	current_activity = pull_activity_dict(activity_selected, data)
	return render_template('collect_info.html', current_activity=current_activity)

photos = UploadSet('photos', IMAGES)
app.config['UPLOADED_PHOTOS_DEST'] = basedir / 'static' / 'long_term_storage' / 'uploads'
configure_uploads(app, photos)

@app.route('/confirm_info', methods=['POST'])
def confirm_info():
	family = request.cookies.get('family')
	data = grab_from_storage(family, basedir)
	activity_selected = request.form['activity_selected']
	print(family)
	print(activity_selected)
	current_activity = pull_activity_dict(activity_selected, data)
	try:
		details_input_data = request.form['details_input']
		print('details_input: ' + details_input_data)
		current_activity['details_input'] = details_input_data
	except:
		pass


	all_form_data = request.form
	print(all_form_data)
	photo_target = basedir / 'static' / 'long_term_storage' / family
	print(photo_target)
	if request.method == 'POST' and 'photo' in request.files:
		try:
			filename = photos.save(request.files['photo'])
			print(filename)
			alert_box_class = 'nice_message'
			results = 'SUCCESS! If you would like to upload another, please do so now.'
		except:
			alert_box_class = 'error_message'
			results = 'You have tried to upload a filetype other than PNG, please try again.'
			return render_template('collect_info.html', results=results, alert_box_class=alert_box_class)

	photo_description = '-' + request.form['photo_description']
	print('photo description: ' + photo_description)
	recent_photo_location = basedir / 'static' / 'long_term_storage' / 'uploads' / filename
	current_suffix = recent_photo_location.suffix
	print(recent_photo_location)
	photo_name = current_activity['Activity'].replace(" ", "_")
	photo_name = photo_name[:20]
	photo_name_plus_description = photo_name + photo_description + current_suffix
	recent_photo_new_name = basedir / 'static' / 'long_term_storage' / 'uploads' / photo_name_plus_description
	recent_photo_new_location = basedir / 'static' / 'long_term_storage' / family / 'photos' / photo_name_plus_description
	os.rename(recent_photo_location, recent_photo_new_name)
	with recent_photo_new_location.open(mode='xb') as f:
		f.write(recent_photo_new_name.read_bytes())
	recent_photo_new_name.unlink()

	if 'photo_list' not in current_activity:
		current_activity['photo_list'] = []
		print('created photo_list list')
	current_activity['photo_list'].append(photo_name_plus_description)
	size = 300, 300

	thumbnail_name_plus_description = photo_name + photo_description + '_thumb' + current_suffix
	recent_photo_new_thumb_location = basedir / 'static' / 'long_term_storage' / family / 'thumbs' / thumbnail_name_plus_description
	im = Image.open(recent_photo_new_location)
	im.thumbnail(size)
	im.save(recent_photo_new_thumb_location)

	if 'thumb_list' not in current_activity:
		current_activity['thumb_list'] = []
		print('created thumb_list list')
	current_activity['thumb_list'].append(thumbnail_name_plus_description)

	first_loop = False
	if current_activity['is_complete'] == False:
		current_activity['is_complete'] = True
		first_loop = True

	if first_loop == True:
		data = configure_score(current_activity, data)

	#update json file with new info
	push_activity_dict(current_activity, data, family, basedir)

	pprint.pprint(current_activity)
	return render_template('collect_info.html', current_activity=current_activity, results=results, alert_box_class=alert_box_class)



if __name__ == '__main__':
	# app.run()
	app.run(debug=True, host='0.0.0.0')
