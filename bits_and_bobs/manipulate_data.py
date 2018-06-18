import csv
import pprint
import json

#reader = csv.DictReader(open('venture_info.csv', 'rb'))

venture_info_dict = {}
venture_info_list = []

print(15 * '\n')

with open('venture_info.csv') as f:
	reader = csv.reader(f)
	data = [r for r in reader]

# with open('venture_info.csv') as f:
# 	reader = csv.DictReader(f)
# 	data = [r for r in reader]

pprint.pprint(data)

keys = ['Number','Category','Activity','Details','Points']
final_dict = {}
for i, data_line in enumerate(data):
	x = int(i)
	i = {}
	i = dict(zip(keys, data_line))
	i['is_complete'] = False
	i['is_target'] = False
	i['details_input'] = ''
	print(i)
	venture_info_dict[x] = i

del venture_info_dict[0]
pprint.pprint(venture_info_dict)

with open('venture_info.json', 'w') as f:
	json.dump(venture_info_dict, f, indent=4)




# pprint.pprint(mini_dict)
