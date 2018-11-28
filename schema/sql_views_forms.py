from django import forms

from .run_raw_sql import run_query
from .choices import roll_no_fields, batch_num_fields, teacher_id_fields, subject_code_fields, semester_fields

class student_subjectForm(forms.Form):
	roll_no = forms.CharField(max_length=12)

	def clean_roll_no(self):
		roll_no = self.cleaned_data['roll_no']
		
		statement = """SELECT * FROM student
						WHERE roll_no='%s';
					"""%(roll_no)
		
		result, error = run_query(statement, get_result=True)

		if(len(result) == 1):	#no records with given roll_no
			raise forms.ValidationError('roll_no ' + str(roll_no) + ' does not exist')

		return roll_no	


class batchSem_studentForm(forms.Form):
	batch = forms.ChoiceField(choices=batch_num_fields)
	semester = forms.ChoiceField(choices=semester_fields)



				
