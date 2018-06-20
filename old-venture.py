from flask import Flask, flash, make_response, render_template, request, redirect, escape, jsonify, Response, url_for
from flask_uploads import UploadSet, configure_uploads, IMAGES
import json
import os
import datetime
import pathlib
from functions import *
from werkzeug.utils import secure_filename
import pprint
from PIL import Image

ALLOWED_EXTENSIONS = set(['jpg', 'jpeg'])

app = Flask(__name__)

basedir = pathlib.Path.cwd()


@app.route('/')
def home():
	return 'You suck'

@app.route('/gregory')
def gregory():
	resp = make_response('howdy')
	resp.set_cookie('family', 'gregory')
	return resp

@app.route('/havens')
def havens():
	resp = make_response('howdy')
	resp.set_cookie('family', 'havens')
	return resp

@app.route('/status')
def status():
	if 'family' in request.cookies:
		family = request.cookies.get('family')
		return 'The family is ' + family
	else:
		return redirect(url_for('home'))

@app.route('/activity_picker')
def activity_picker():
	if 'family' in request.cookies:
		family = request.cookies.get('family')
		data = grab_from_storage(family, basedir)
		return render_template('activity_picker.html', data=data)
	else:
		redirect(url_for('home'))

@app.route('/apply_activity', methods=['POST'])
def apply_activity():
	if 'family' in request.cookies:
		family = request.cookies.get('family')
		data = grab_from_storage(family, basedir)
		activity_selected = request.form['activity_selected']
		current_activity = pull_activity_dict(activity_selected, data)
		return render_template('collect_info.html', current_activity=current_activity)

	else:
		redirect(url_for('home'))

photos = UploadSet('photos', IMAGES)
app.config['UPLOADED_PHOTOS_DEST'] = basedir / 'static' / 'long_term_storage' / 'uploads'
configure_uploads(app, photos)

@app.route('/confirm_info', methods=['POST'])
def confirm_info():
	if 'family' in request.cookies:
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
				return render_template('upload.html', results=results, alert_box_class=alert_box_class)

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

		current_activity['is_complete'] = True

		push_activity_dict(current_activity, data, family, basedir)

		pprint.pprint(current_activity)
		return render_template('collect_info.html', current_activity=current_activity, results=results, alert_box_class=alert_box_class)

	else:
		redirect(url_for('home'))

if __name__ == '__main__':
	# app.run()
	app.run(debug=True, host='0.0.0.0')
