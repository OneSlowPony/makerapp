"""
Note: can be imported like a module to be run from the flask application file or whatever. 

This script loads data from UPLOAD_FOLDER and transforms it into 2 new datastructures (below).
All you need to do is give the last session (+1) that you want data for and the program will return the specified dataframes
as CSV files in a specified folder labelled with the date you pulled them from. 

1. IA totals and emoji feedback 
0-25, 25-50, 50-75, 75-100
loved it, curious, bored, confused

Session    E1    E2    E3    E4    U    A     E    D
1    	   15     2     7     6     4   17    5    4
2    	   19     2     3     6    11    6    9    4
3    	   4     21     4     1    16   10    4    0


2. Each column is a student (a new df. for each session)

Roll    		1    2    3    4    5    6
Emoji    		3    2    4    4    2    4
Understanding   4    1    2    1    4    2
Application     4    1    2    1    4    2
Engagement      5    4    3    4    5    5

limitations: 
pandas is designed to load fully populated dataframes, where as here i'm making lists & then populating dataframes like that
This is why it is much better to have a database system, where we can make queries and create dataframes from that -
but it's okay for now. Also, I think this code is at times very "brute force" like, and not that elegant. 
Am still brainstoring solutions to make it (much) more efficient and truly take advantage of pandas 

"""

import csv
import os 
import pandas as pd
import numpy as np

#-------------------------------------------------------------------------------------------------------------------
# GLOBAL VARIABLES: 
#-------------------------------------------------------------------------------------------------------------------

#folder to search data
UPLOAD_FOLDER = '/Users/sabamundlay/Desktop/firstjob/dashboard_development/datafromflaskapp'

#to store new dataframes into 
RETURN_FOLDER = '/Users/sabamundlay/Desktop/firstjob/dashboard_development/datafromflaskapp'

#stores contents of files for all sessions specified 
IA_LIST = []
METADATA_LIST = []
EMOJI_LIST = []

#-------------------------------------------------------------------------------------------------------------------
# INTERNAL FUNCTIONS: 
#-------------------------------------------------------------------------------------------------------------------

#takes a directory & returns filepaths
def get_filepaths(directory):
	filepaths = []
	for root, directories, files in os.walk(folderpath):
		for filename in files:
			filepath = os.path.join(root, filename)
			filepaths.append(filepath)
	return filepaths

#takes a filepath & returns the content in the form of a dataframe
def get_filecontent(file_path):
	with open(file_path) as f:
		df = pd.read_csv(f)
		return df

#adds to global metadata list 
def add_to_meta(file_path):
	with open(file_path) as f:
		
		#skips the row of headers
		f.next()
		for row in f:
			s = row.split(',')
			tempdict = {
				'session_num': s[1],
				'session_date': s[2],
				'session_length': s[3],
				'assessment': s[4],
				'makerlookfor': s[5].rstrip("\r\n"),
			}

			METADATA_LIST.append(tempdict)

#adds to global ia data list 
def add_to_ia(file_path):
	with open(file_path) as f:
		f.next()
		for row in f:
			s = row.split(',')
			tempdict = {
				'student_id': s[0],
				'first_name': s[1],
				'last_name': s[2],
				'understanding': s[3],
				'application': s[4],
				'design': s[5],
				'planning': s[6],
				'engagement': s[7].rstrip("\r\n"),
			}
			
			IA_LIST.append(tempdict)

#adds to the global emoji list
def add_to_emoji(file_path):
	with open(file_path) as f:
		f.next()
		for row in f:
			s = row.split(',')
			tempdict = {
				'session_num': s[0],
				'student_id': s[1],
				'emoji': s[2],
			}
		
			EMOJI_LIST.append(tempdict)

#turns lists into dataframes
def make_df(complete_list):
	#complete_list is a list of dict. objects, where dict. keys become headers in the dataframe
	df = pd.DataFrame.from_dict(complete_list)
	return df

#creates the first datastructure, which keeps track of total counts for each session
def create_datastructure1(ia, emoji_data):
	
	#makes sure we have the same amount of data from individal assesment list & emoji list
	if (ia.last_valid_index() != emoji_data.last_valid_index()):
		return "ERROR: check fileupload to list to dataframe functionality"
	
	else:
		#dict objects will be added to this master list, and list will be passed to make_df(COUNTS_LIST)
		COUNTS_LIST = []
		
		#use for indexing
		start = 0
		end = 21
		
		#keep track of which session we will index for
		session_count = 1

		#variables for every dict object
		bin1 = 0
		bin2 = 0
		bin3 = 0
		bin4 = 0
		e1 = 0
		e2 = 0
		e3 = 0
		e4 = 0
		
		#group the columns we want to convert to integers
		colsIA = list(ia)
		colsIA.remove('student_id')
		colsIA.remove('first_name')
		colsIA.remove('last_name')

		#convert certain columns from string to numeric in ia df
		for i in colsIA:
			ia[i] = pd.to_numeric(ia[i], errors='coerce')

		#calculate totals of the 5 measures & append to the ia dataframe
		ia['totals'] = ia[colsIA].sum(numeric_only=True, axis=1)

		#convert emoji value to numeric
		emoji_data['emoji'] = pd.to_numeric(emoji_data['emoji'], errors='coerce')

		while (end <= ia.last_valid_index()):
			
			#create a temporary index of 21 values to represent a session 
			tempindexIA = ia.ix[ia.index[start:end], ['totals']]
			tempindexEMOJI = emoji_data.ix[emoji_data.index[start:end], ['emoji']]

			#iterate through the totals column, updating bin1 - bin4
			for total in tempindexIA['totals']:
				if total <= 24:
					bin1 = bin1 + 1
				elif total >= 25 and total <= 49:
					bin2 = bin2 + 1
				elif total >= 50 and total <= 74:
					bin3 = bin3 + 1
				else:
					bin4 = bin4 + 1

			#iterate through the emoji column, updating the counts for e1 - e4
			for emoji in tempindexEMOJI['emoji']:
				if emoji == 1:
					e1 = e1 + 1
				elif emoji == 2:
					e2 = e2 + 1
				elif emoji == 3:
					e3 = e3 + 1
				elif emoji == 4:
					e4 = e4 + 1

			#add to the list as one row in the new dataframe
			tempdict = {
				'session_num': session_count,
				'bin1': bin1,
				'bin2': bin2,
				'bin3': bin3,
				'bin4': bin4,
				'e1': e1,
				'e2': e2,
				'e3': e3,
				'e4': e4,
			}
			
			COUNTS_LIST.append(tempdict)
			
			#update
			start = end + 1
			end = start + 21
			session_count = session_count + 1
			
			#reset
			bin1 = 0
			bin2 = 0
			bin3 = 0
			bin4 = 0
			e1 = 0
			e2 = 0
			e3 = 0
			e4 = 0

		#make a dataframe from the full list of totals
		countdf = make_df(COUNTS_LIST)

	
	#store into one csv in specified return folder
	#try:
	#	return True
	#except:
	#	return False
	
	#return the dataframe keeping track of total counts for every session 
	return countdf

def create_datastructure2(ia, emoji_data):
	
	if (ia.last_valid_index() != emoji_data.last_valid_index()):
		return "ERROR: check fileupload to list to dataframe functionality"
	else:
		ALL_SESSIONS = []

		#keep track of which session we are indexing
		session_count = 0
		
		#keep track of indexing
		start = 0
		end = 22

		#group the columns we want to convert to integers
		colsIA = list(ia)
		colsIA.remove('student_id')
		colsIA.remove('first_name')
		colsIA.remove('last_name')

		#convert certain columns from string to numeric in ia df
		for i in colsIA:
			ia[i] = pd.to_numeric(ia[i], errors='coerce')

		#convert emoji value to numeric
		emoji_data['emoji'] = pd.to_numeric(emoji_data['emoji'], errors='coerce')

		while(end <= ia.last_valid_index()):

			#list of individual students dict objects (new list for every session)
			STUDENTS = []
			emojilist = []
			
			#create temporary index
			tempindexIA = ia.loc[ia.index[start:end]]
			tempindexEMOJI = emoji_data.loc[emoji_data.index[start:end]]

			#create a new dataframe for a single student (just individual assessment data right now) 
			for index, row in tempindexIA.iterrows():
				singlestudent = row.to_frame()
				tempdict = {
				'application': singlestudent[index][0],
				'design' : singlestudent[index][1],
				'engagement' : singlestudent[index][2],
				'planning' : singlestudent[index][5],
				'understanding': singlestudent[index][7],
				'student_id' : singlestudent[index][6],
				}
				STUDENTS.append(tempdict)

			#append the correct emoji data
			for index, row in tempindexEMOJI.iterrows():
				singleemoji = row.to_frame()
				emojidict = {
				'emoji' : singleemoji[index][0],
				'studentid' : singleemoji[index][2]
				}
				emojilist.append(emojidict)

			#iterate through the emojilist
			for i in range (0, len(STUDENTS)):
				for j in range (0, len(emojilist)):
					a = emojilist[j]['studentid']
					b = STUDENTS[i]['student_id']
					if (a == b):
						#add it to correct dictionary object 
						STUDENTS[i]['emoji'] = emojilist[i]['emoji']

			
			#list of students & their specific values for one session
			session_dataframe = make_df(STUDENTS)
			session_dataframe = session_dataframe.transpose()
			ALL_SESSIONS.append(session_dataframe)

			#update
			start = end
			end = start + 22
			session_count = session_count + 1

	#store into multiple, one for each session
	#try:
		#loop over the list & write to CSV keeping track of session count (tells you how many sessions we've interated through)
		#return True
	#except:
	#	return False
	
	return ALL_SESSIONS

#-------------------------------------------------------------------------------------------------------------------
# MAIN: (code that executes when this file is imported as a module)
#-------------------------------------------------------------------------------------------------------------------
														
user_input = raw_input('Get data uptil & including session number: ')
session_range = range(1, (int(user_input) + 1))														

for i in session_range: 
	foldername = 'session_%s' % str(i)
	folderpath = os.path.join(UPLOAD_FOLDER, foldername)
	full_file_paths = get_filepaths(folderpath)
	
	#this is a big weakness...
	#the whole program will break if this dictionary does not actually point to the correct files in the correct order.
	contents = dict([ ('emoji', full_file_paths[0]), ('ia', full_file_paths[1]), ('metadata', full_file_paths[2])])
	#contnets = dict([('emoji', full_file_paths[0]), ('metadata', full_file_paths[2])])


	#add the contents of the selected files to master lists
	add_to_meta(contents['metadata'])
	add_to_ia(contents['ia'])
	add_to_emoji(contents['emoji'])

#make pandas dataframes from those master lists
individual_assessmment = make_df(IA_LIST)
session_metadata = make_df(METADATA_LIST)
emoji_data = make_df(EMOJI_LIST)

#create the two datastructures & store them in csv format in a folder
counts_datastructure = create_datastructure1(individual_assessmment, emoji_data)
rollnum_datastructure = create_datastructure2(individual_assessmment, emoji_data)

counts_datastructure.to_csv("/Users/sabamundlay/Desktop/firstjob/dashboard_development/datafromflaskapp/test.csv")
count = 0
for i in rollnum_datastructure:
	newfile = "/Users/sabamundlay/Desktop/firstjob/dashboard_development/datafromflaskapp/"+ "%stest.csv" % count
	i.to_csv(newfile)
	count = count + 1
	#i.to_csv("/Users/sabamundlay/Desktop/firstjob/dashboard_development/datafromflaskapp/test%s.csv" % i)
#print rollnum_datastructure

#if (counts_datastructure and rollnum_datastructure == True):
#	print "Your NEW datastructures have been stored at: " #+ RETURN_FOLDER
#else:
#	print "there was some error"





