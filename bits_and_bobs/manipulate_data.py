import csv
import pprint
import json



venture_info_dict = {}


print(15 * '\n')

with open('venture_info.csv') as f:
	reader = csv.reader(f)
	data = [r for r in reader]

#pprint.pprint(data)

data.pop(0)
data.insert(0, ['3', 'nope', 'nope', 'nope', '4'])

for line in data:
	line[0] = int(line[0])
	line[4] = int(line[4])

keys = ['Number', 'Category', 'Activity', 'Details', 'Points']
final_dict = {}
for i, data_line in enumerate(data):

	# x = {}
	x = dict(zip(keys, data_line))
	x['is_complete'] = False
	x['is_target'] = False
	x['details_input'] = ''
	x['show']=''
	#print(x)
	venture_info_dict[int(i)] = x

del venture_info_dict[0]
pprint.pprint(venture_info_dict)

# output_dict = {}
# for key, value in venture_info_dict:
#     output_dict[int(key)] = [item for item in value]

# print(output_dict)

venture_info_dict['score'] = {
							"total_score": 0,
							"categories": {
								"Get Moving": {
									"completed": 0,
									"needed": 3
								},
								"Investigate": {
									"completed": 0,
									"needed": 2
								},
								"Serve": {
									"completed": 0,
									"needed": 2
								},
								"Outdoor Skills": {
									"completed": 0,
									"needed": 3
								},
								"Create": {
									"completed": 0,
									"needed": 2
								},
								"Just For Fun": {
									"completed": 0,
									"needed": 3
								},
								"Know Your Parks": {
									"completed": 0,
									"needed": 3
								},
								"Weekly Bonus Activity": {
									"completed": 0,
									"needed": 0}
							}}

with open('venture_info.json', 'w') as f:
	json.dump(venture_info_dict, f, indent=4)




# pprint.pprint(mini_dict)
