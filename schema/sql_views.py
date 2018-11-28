from os import remove

from django.shortcuts import render
from django.http import HttpResponse

from .run_raw_sql import run_query
from .sql_views_forms import *

try:
	from openpyxl import Workbook
	EXCEL_SUPPORT = True
except:
	EXCEL_SUPPORT = False

VIEWS_DESCRIPTION = {
					'batchSem_student': 'List all the student names along with their electives for a given batch and semester',
					}

def batchSem_student(request):

	def group_Records(result):
		#print(final_list)
		final_list = [result[0] + ['count']]
		curr_sub_code = result[1][0]
		curr_sub_name = result[1][1]
		curr_teacher_id = result[1][2]
		curr_teacher_name = result[1][3]
		aggr_roll_no = [result[1][4]]
		aggr_student_name = [result[1][5]]

		for record in result[2:]:
			if record[0] == curr_sub_code:
				aggr_roll_no.append(record[4])
				aggr_student_name.append(record[5])
			else:
				final_list.append([curr_sub_code, curr_sub_name, curr_teacher_id, curr_teacher_name, aggr_roll_no, aggr_student_name, len(aggr_roll_no)])
				curr_sub_code = record[0]
				curr_sub_name = record[1]
				curr_teacher_id = record[2]
				curr_teacher_name = record[3]
				aggr_roll_no = [record[4]]
				aggr_student_name = [record[5]]

		final_list.append([curr_sub_code, curr_sub_name, curr_teacher_id, curr_teacher_name, aggr_roll_no, aggr_student_name, len(aggr_roll_no)])

		return final_list

	def convert2Excel(result):
		wb = Workbook()
		ws = wb.active

		ws.append(result[0])

		for row in result[1:]:
			buff = ['\n'.join(elem) if isinstance(elem, list) else elem for elem in row]
			ws.append(buff)

		wb.save(fileName)


	result = error = None

	if request.method == 'POST':
		form = batchSem_studentForm(request.POST)

		if form.is_valid():
			batch = form.cleaned_data['batch']
			semester = form.cleaned_data['semester']
			statement = """SELECT subject.subject_code AS Subject_Code, subject.name AS Subject_Name, teache.teacher_id as Teacher_ID,
							teache.first_name||' '||teache.middle_name||' '||teache.last_name as teacher, roll_no AS Roll_no,
							student.first_name||' '||student.middle_name||' '||student.last_name AS student_name
							FROM student NATURAL JOIN (SELECT batch_num, roll_no FROM belongs_to) AS belongs NATURAL JOIN
							subject NATURAL JOIN (SELECT roll_no, subject_code, semester FROM chooses) AS choose INNER JOIN (SELECT * FROM teacher NATURAL JOIN teaches) AS teache
							ON choose.subject_code=teache.subject_code AND choose.semester=teache.semester AND belongs.batch_num=teache.batch_num
							WHERE teache.batch_num='%s' AND teache.semester='%s'
							ORDER BY Subject_Code;
						"""%(batch, semester)

			result, error = run_query(statement, get_result=True)

			if result and len(result) > 1:	
				result = group_Records(result)

			
			for ind,record in enumerate(result):
				if request.POST.get(str(ind)):
					fileName = batch + '_' + semester + '_' + record[0] + '.xlsx'
					convert2Excel([result[0], record])
					file = open(fileName, 'rb')
					response = HttpResponse(file, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
					response['Content-Disposition'] = 'attachment; filename=%s'%(fileName)
					remove(fileName)
					return response

			if request.POST.get('submit_getExcel'):
				fileName = batch+'_'+semester+'.xlsx'
				convert2Excel(result)
				file = open(fileName, 'rb')
				response = HttpResponse(file, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
				response['Content-Disposition'] = 'attachment; filename=%s'%(fileName)
				remove(fileName)
				return response

	else:
		form = batchSem_studentForm()

	return render(request, 'sql_views.html', {'form': form, 'error': error, 'result': result, 'excel_support': EXCEL_SUPPORT})
	

def sql_view(request, viewName=None):
	error = None
	if viewName:
		if (viewName in VIEWS_DESCRIPTION):
			return globals()[viewName](request)
		else:
			error = 'SQL View ' + viewName + ' does not exist'

	return render(request, 'sql_views.html', {'error': error, 'views_list': VIEWS_DESCRIPTION})