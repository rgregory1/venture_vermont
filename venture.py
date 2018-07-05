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

# basedir = pathlib.Path.cwd()
# alt base directory to try
basedir = pathlib.Path(__file__).parent.resolve()


photos = UploadSet('photos', IMAGES)
app.config['UPLOADED_PHOTOS_DEST'] = basedir / \
	'static' / 'long_term_storage' / 'uploads'
configure_uploads(app, photos)


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
						resp = make_response(render_template(
							'login_form.html', alert_box_class=alert_box_class, results=results))
						print('created response')
						resp.set_cookie('family', login_creds[user]['family_cookie'])
						print('createde cookie')

						# return render_template('login_form.html', alert_box_class=alert_box_class, results=results)
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
	return render_template('collect_info.html', current_activity=current_activity, data=data)


@app.route('/confirm_info', methods=['POST'])
@cookie_required
def confirm_info():
	# get user info from cookies
	family = request.cookies.get('family')
	# get data from json file for family
	data = grab_from_storage(family, basedir)
	# grab activity to modify from form
	activity_selected = request.form['activity_selected']
	# testing to see if everything is working
	# print(family)
	# print(activity_selected)
	# grab current complted dictionary of activity info from json data
	current_activity = pull_activity_dict(activity_selected, data)
	# Test to see if there was a details field in the current activity
	try:
		# if details are present, assign them to a key in the dict
		details_input_data = request.form['details_input']
		current_activity['details_input'] = details_input_data
		details_input_data = details_input_data.replace(" ", "_")
		details_input_data = '-' + details_input_data
	except:
		# if no details are present, bypass this without breaking
		details_input_data = ''

	# testing to see what data is passed from form
	# all_form_data = request.form
	# print(all_form_data)

	# setting up photo_target variable to save photos for each family
	photo_target = basedir / 'static' / 'long_term_storage' / family
	# print(photo_target)
	if request.method == 'POST' and 'photo' in request.files:
		# insure that it is a photo that is uploaded
		try:
			filename = photos.save(request.files['photo'])
			print(filename)
			alert_box_class = 'happy'
			results = 'SUCCESS! If you would like to upload another, please do so now.'
		except:
			# return an error message if it isn't a photo
			alert_box_class = 'error_message'
			results = 'You have tried to upload a filetype other than a photo, please try again.'
			return render_template('collect_info.html', results=results, alert_box_class=alert_box_class)

	# grab photo description from form, add a hypen to it
	photo_description = request.form['photo_description']
	if photo_description != '':
		photo_description = photo_description.replace(" " ,"_")
		photo_description = '-' + photo_description
	# print('photo description: ' + photo_description)
	# create path for photo in default uploads folder
	recent_photo_location = basedir / 'static' / 'long_term_storage' / 'uploads' / filename
	#find the file extension of the uploaded photos
	current_suffix = recent_photo_location.suffix
	# print(recent_photo_location)
	# replace all spaces in names with underscores
	photo_name = current_activity['Activity'].replace(" ", "_")
	# reduce the name to the first 20 characters in the activity name
	photo_name = photo_name[:20]
	# create new filename
	photo_name_plus_description = photo_name + details_input_data + photo_description +  current_suffix


	# when changing name of photo, this will be the new name
	recent_photo_new_name = basedir / 'static' / 'long_term_storage' / 'uploads' / photo_name_plus_description
	# creating variable with new name and new location
	recent_photo_new_location = basedir / 'static' / 'long_term_storage' / family / 'photos' / photo_name_plus_description
	# change name of photo uploaded in uploads folder to name constructed from form info
	os.rename(recent_photo_location, recent_photo_new_name)
	# copy photo to family storage folder

	# test to see if planned new location filename is already in use
	if recent_photo_new_location.is_file():
		print('file already exists')
		counter = 1
		looking_for_increment = True
		while looking_for_increment:
			trial_location = recent_photo_new_location.stem + str(counter)
			print(trial_location)
			new_file_name = trial_location + current_suffix
			second_trial_location = basedir / 'static' / 'long_term_storage' / family / 'photos' / new_file_name
			counter += 1
			if second_trial_location.is_file():
				pass
			else:
				recent_photo_new_location = second_trial_location
				looking_for_increment = False

	print('past the loop')
	with recent_photo_new_location.open(mode='xb') as f:
		f.write(recent_photo_new_name.read_bytes())
	# cleanup - delete uploaded folder from uploads folder
	recent_photo_new_name.unlink()

	if 'photo_list' not in current_activity:
		current_activity['photo_list'] = []
		print('created photo_list list')
	current_activity['photo_list'].append(photo_name_plus_description)
	size = 300, 300

	main_photo_name = recent_photo_new_location.stem
	thumbnail_name_plus_description = main_photo_name + '_thumb' + current_suffix
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

	# update json file with new info
	push_activity_dict(current_activity, data, family, basedir)

	pprint.pprint(current_activity)
	return render_template('collect_info.html', current_activity=current_activity, results=results, alert_box_class=alert_box_class, data=data)

@app.route('/completed')
@cookie_required
def completed():
	family = request.cookies.get('family')
	data = grab_from_storage(family, basedir)
	return render_template('completed.html', data=data, family=family)

@app.route('/priority_picker')
@cookie_required
def priority_picker():
	family = request.cookies.get('family')
	data = grab_from_storage(family, basedir)
	return render_template('priority_picker.html', data=data, family=family)

@app.route('/priority_processor', methods=['POST'])
@cookie_required
def priority_processor():
	family = request.cookies.get('family')
	priority_toggles = request.form.getlist('priority_toggle')
	data = grab_from_storage(family, basedir)

	print(priority_toggles)

	for toggle in priority_toggles:
		for activity in data:
			print(toggle)
			print(data[activity]['Activity'])
			if toggle == data[activity]['Activity']:
				if data[activity]['is_target'] == False:
					print(data[activity]['Activity'] + ' is false')
					data[activity]['is_target'] = True
					print(data[activity]['Activity'] + ' has been toggled')
				else:
					data[activity]['is_target'] = False
					print(data[activity]['Activity'] + ' is truey')
					print(data[activity]['Activity'] + ' has been toggled')
				print('breaking now')
				break

	push_dict(data, family, basedir)
	# update json file with new info
	# push_activity_dict(current_activity, data, family, basedir)
	return redirect(url_for('priority_list'))

@app.route('/priority_list')
@cookie_required
def priority_list():
	family = request.cookies.get('family')
	data = grab_from_storage(family, basedir)
	# total priority list points here
	priority_points = find_priority_points_total(data)
	return render_template('priority_list.html', data=data, priority_points=priority_points)

@app.route('/add_bonus', methods=['GET', 'POST'])
@cookie_required
def add_bonus():
	family = request.cookies.get('family')
	data = grab_from_storage(family, basedir)
	return render_template('collect_bonus_info.html', data=data)

@app.route('/confirm_bonus_info', methods=['GET', 'POST'])
@cookie_required
def confirm_bonus_info():
	current_activity = {}
	family = request.cookies.get('family')
	data = grab_from_storage(family, basedir)
	# grab the name of the bonus activity
	activity_selected = request.form['bonus_activity_name']
	# print('activity selected: ' + activity_selected)
	bonus_activity_points = int(request.form['bonus_activity_points'])
	# print('bonus points: ' + bonus_activity_points)
	# grab photo description from form, add a hypen to it
	# photo_description = request.form['photo_description']
	# if photo_description != '':
	# 	photo_description = photo_description.replace(" " ,"_")
	# 	photo_description = '-' + photo_description
	# print('photo description: ' + photo_description)

	current_activity['Category'] = 'Bonus Activities'
	current_activity['Activity'] = activity_selected
	current_activity['Details'] = ''
	current_activity['Points'] = bonus_activity_points
	current_activity['is_complete'] = False
	current_activity['is_target'] = False
	current_activity['details_input'] = ''

	pprint.pprint(current_activity)
	data_length = len(data) - 78
	print('data length: ' + str(data_length))
	bonus_number = 'B' + str(data_length)
	# figure out length of dictionary then subtract one and concatitnate it with B to get
	# the dictionary key
	data[bonus_number] = current_activity
	push_dict(data, family, basedir)
	return redirect(url_for('activity_picker'))

if __name__ == '__main__':
	# app.run()
	app.run(debug=True, host='0.0.0.0')
