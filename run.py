'''
This application will run on localhost:5000 by default. You can change this at the bottom, by specifying a new server & port in app.run().
It will present the user with an HTML form for them to do 4 things. It then stores those files in a folder you specify. 
For security reasons, keep this folder outside of your application root directory 

BEFORE RUNNING: 
Set the absolute path that you want to save your files to by changing the UPLOAD_FOLDER variable. 
Lastly, make sure you are working in a virtual environment that has flask, werkzeug & pandas installed. 

FEATURES: 
checks is file is CSV, sets max file size, secures filenames (follows a naming protocol), checks that no field is empty 


'''

import os
import csv
from flask import Flask, request, render_template, jsonify, g
from werkzeug.utils import secure_filename
import pandas as pd

#successful file uploads will be saved here
UPLOAD_FOLDER = '/Users/sabamundlay/Desktop/firstjob/dashboard_development/datafromflaskapp'
#only csv files allowed
ALLOWED_EXTENSIONS  = set(['csv'])
#total file size cannot exceed one megabyte
MAX_CONTENT_LENGTH = 1 * 1024 * 1024

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS

#whitelist to limit file uploads of the wrong type
def isCSV(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods= ['GET', 'POST'])
@app.route('/upload', methods = ['GET', 'POST'])
def upload():

	if request.method == 'POST':
		
		#COLLECT SESSION METADATA
		session_num = request.form['session_num']
		session_date = request.form['session_date']
		session_length = request.form['session_length']
		assessment = request.form['assessment']
		makerlookfor = request.form['makerlookfor']

		#CHECK THAT SESSION DATE IS NOT EMPTY
		if not session_date:
			response = "ERROR: please remember to include the session date."
			return render_template('responses.html', response=response)

		raw_data = {
		'session_num':[session_num],
		'session_date': [session_date],
		'session_length': [session_length],
		'assessment': [assessment],
		'makerlookfor': [makerlookfor],
		}

		newpath = UPLOAD_FOLDER + "/" + 'session_%s' % session_num
		if not os.path.exists(newpath):
			os.makedirs(newpath)
		
		#WRITE METADATA TO CSV
		newfile = newpath + "/" + 'Session%sMetadata.csv' % session_num
		df = pd.DataFrame(raw_data, columns=['session_num', 'session_date', 'session_length', 'assessment', 'makerlookfor'])
		df.to_csv(newfile, index = True)

		#COLLECT UPLOADED FILES
		uploaded_files = request.files.getlist("file[]")
		filenames = []
		
		for file in uploaded_files:
			#CHECK IF FILE LIST NOT EMPTY, AND FILES END IN .CSV
			if file and isCSV(file.filename):
				
				if "emoji" in file.filename:
					filename = 'emoji_feedback.csv'
				
				elif "individual" in file.filename:
					filename = 'individual_assessment.csv'
				
				#SECURE FILENAME IF NOT MANUALLY CHANGING IT
				else:
					filename = secure_filename(file.filename)
				
				#SAVE FILES TO SPECIFIED FOLDER
				file.save(os.path.join(newpath, filename))
				filenames.append(filename)

			else:
				response = "ERROR: please upload ONLY csv files."
				return render_template('responses.html', response=response)
		
		response = "SUCCESS: your files have been saved."
		return render_template('responses.html', response=response)
	
	else:
		return render_template('upload.html')

if __name__ == "__main__":
	app.run(debug=True)

