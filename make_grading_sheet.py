from canvasapi import Canvas
import time 
from datetime import datetime, timedelta
import csv

# Canvas API URL
API_URL = "https://courseworks2.columbia.edu/api/v1/"
# Canvas API key
API_KEY = "API_KEY_GOES_HERE"
GRACE_PERIOD_HOURS = 0
COURSE_ID = 'COURSE_ID_GOES_HERE'
ASSIGNMENT_ID = 'ASSIGNMENT_ID_GOES_HERE'

#write assignment due date following example form below
assignment_deadline = datetime.strptime('2017-11-27-23:59:00', "%Y-%m-%d-%H:%M:%S")
#change hours to whatever your classes grace period is 
due_date = assignment_deadline + timedelta(hours=GRACE_PERIOD_HOURS)
#make sure to change this to timezone you need
GMT_EST_TIME_DIFFERENCE = 5
# Initialize a new Canvas object
canvas = Canvas(API_URL, API_KEY)

def get_submission_times(course_id, assignment_id):
	result_dict = {}
	course = canvas.get_course(course_id)
	submissions = course.list_submissions(assignment_id)
	late = 0
	on_time = 0
	for submission in submissions:
		if submission.submitted_at is None:
			output = (submission.user_id, True)
			result_dict[str(submission.user_id)] = True
		else:
			if submission.late:
				late +=1 
				cleaned_date = clean_date(submission.submitted_at) 
				east_time = cleaned_date - timedelta(hours=GMT_EST_TIME_DIFFERENCE)
				if past_grace_period_late(east_time):
					output = (submission.user_id, True)
					result_dict[str(submission.user_id)] = True
				else:
					output = (submission.user_id, False)
					result_dict[str(submission.user_id)] = False
			else:
				on_time +=1
				output = (submission.user_id, False)
				result_dict[str(submission.user_id)] = False
	print("Here are the results: " + str(on_time) + " submitted this assignment on time and " + str(late) + " submitted it late.")
	return result_dict

def output_result(output_list):
	with open('output.csv','w') as out:
		csv_out=csv.writer(out)
		csv_out.writerow(['Name', 'ID', 'UNI', 'Late (TRUE/FALSE)'])
		for row in output_list:
			csv_out.writerow(row)

def clean_date(submit_time):
	submit_time = submit_time.replace('T', '-')
	submit_time = submit_time.replace('Z', '')
	return datetime.strptime(submit_time, "%Y-%m-%d-%H:%M:%S")

def past_grace_period_late(submit_time):
	return submit_time >= due_date

def merge_data(student_grades, submission_dict):
	result = []
	for row in student_grades:
		row = row.strip()
		row_list = row.split(",")
		name = row_list[0] + "," + row_list[1]
		canvas_id = str(row_list[2])
		uni = row_list[3]

		if canvas_id in submission_dict.keys():
			output = (name, canvas_id, uni, submission_dict[row_list[2]])
			result.append(output)
		else:
			pass
	result.sort(key=lambda tup: tup[2])
	return result

def main():
	#returns a dict where key is canvas id and value is boolean for whether assignment was late
	submission_dict = get_submission_times(COURSE_ID, ASSIGNMENT_ID)
	#relies on you including file of student grades from grades section and renaming it grades.csv
	try:
		student_grades = open('grades.csv', 'r')
	except:
		print("Failed to find grades.csv file")
		return -1
	output_result_list = merge_data(student_grades, submission_dict)
	#outputs grading sheet to current directory as output.csv 
	return output_result(output_result_list)
main()