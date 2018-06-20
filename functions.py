import pathlib
import json

# basedir = pathlib.Path.cwd()

def grab_from_storage(family, basedir):
	"""grabs initial dict from json file in temp folder"""
	suffix = '.json'
	family_file = family + suffix
	target_directory = basedir / 'static' / 'long_term_storage' / family / family_file
	print(target_directory)
	with open(target_directory) as f:
		initial_family_data = json.load(f)
	return initial_family_data


def pull_activity_dict(activity_selected, data):
	current_activity = {}
	for activity in data:
		if data[activity]['Activity'] == activity_selected:
			current_activity = data[activity]
			break
	return current_activity

def reconfigure_score(data):
	data['score']['total_score'] = 0
	for activity in data:
		if 'Category' in activity:
			if data[activity]['is_complete'] == True:
				data['score']['total_score'] = data['score']['total_score'] + data[activity]['Points']


	return data

def configure_score(current_activity, data):
	data['score']['total_score'] = data['score']['total_score'] + current_activity['Points']
	for category in data['score']['categories']:
		print(data['score']['categories'][category])
		print(current_activity['Category'])
		print(category)
		if category == current_activity['Category']:
			data['score']['categories'][category]['completed'] += 1
			break
	return data

def push_activity_dict(current_activity, data, family, basedir):
	for activity in data:
		if data[activity]['Activity'] == current_activity['Activity']:
			data[activity] = current_activity
			break
	suffix = '.json'
	family_file = family + suffix
	target_directory = basedir / 'static' / 'long_term_storage' / family / family_file
	with open(target_directory, 'w') as f:
		json.dump(data, f, indent=4)

def push_dict(data, family, basedir):
	suffix = '.json'
	family_file = family + suffix
	target_directory = basedir / 'static' / 'long_term_storage' / family / family_file
	with open(target_directory, 'w') as f:
		json.dump(data, f, indent=4)
