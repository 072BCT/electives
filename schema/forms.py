from django import forms

from .models import *
from .run_raw_sql import run_query
from .choices import *


class QueryForm(forms.Form):
    query = forms.CharField(label='SQL Query', widget=forms.Textarea)


class studentForm(forms.ModelForm):
	batch = forms.ChoiceField()

	def __init__(self, *args, **kwargs):
		super(studentForm, self).__init__(*args, **kwargs)
		self.fields['batch'].choices = batch_num_fields()

	class Meta:
		model = student
		fields = '__all__'

	def clean_roll_no(self):
		roll_no = self.cleaned_data['roll_no']

		try:
			split_txt = roll_no.split('/')
			t1 = split_txt[0].isdigit() and len(split_txt[0])==3
			t2 = str.isalpha(split_txt[1]) and len(split_txt[1])==4
			t3 = split_txt[2].isdigit() and (len(split_txt[2])==3)

			if not (t1 and t2 and t3):
				raise forms.ValidationError("Mismatch format for roll_no. Example: 072/MSCS/111")

			roll_no = split_txt[0] + '/' + split_txt[1].upper() + '/' + split_txt[2]

		except Exception as e:
			raise forms.ValidationError("Mismatch format for roll_no. Example: 072/MSCS/111")

		return roll_no


class subjectForm(forms.ModelForm):
	
	class Meta:
		model = subject
		fields = '__all__'


class batchForm(forms.ModelForm):
	
	class Meta:
		model = batch
		fields = '__all__'


class teacherForm(forms.ModelForm):
	
	class Meta:
		model = teacher
		fields = '__all__'


class belongs_toForm(forms.Form):
	roll_no = forms.ChoiceField(label='Student')
	batch_num = forms.ChoiceField(label='Batch')
	
	def __init__(self, *args, **kwargs):
		super(belongs_toForm, self).__init__(*args, **kwargs)
		self.fields['batch_num'].choices = batch_num_fields()
		self.fields['roll_no'].choices = roll_no_fields()

	def clean(self):
		roll_no = self.cleaned_data['roll_no']
		batch_num = self.cleaned_data['batch_num']
		query = """SELECT * FROM belongs_to
					WHERE roll_no='%s' AND batch_num='%s';
				"""%(roll_no, batch_num)
		result, error = run_query(query, get_result=True)

		if len(result) > 1:	#record already exists:
			raise forms.ValidationError('Record with roll_no ' + roll_no + ' and batch_num ' + batch_num + ' already exists')


class teachesForm(forms.Form):
	teacher_id = forms.ChoiceField(label='Teacher')
	subject_code = forms.ChoiceField(label='Subject')
	batch_num = forms.ChoiceField(label='Batch')
	semester = forms.ChoiceField()

	def __init__(self, *args, **kwargs):
		super(teachesForm, self).__init__(*args, **kwargs)
		self.fields['batch_num'].choices = batch_num_fields()
		self.fields['subject_code'].choices = subject_code_fields()
		self.fields['teacher_id'].choices = teacher_id_fields()
		self.fields['semester'].choices = semester_fields()

	def clean_semester(self):
		semester = self.cleaned_data['semester']
		if semester not in ('1','2','3','4'):
			raise forms.ValidationError("Semester should be either 1, 2, 3 or 4")

		return semester

	def clean(self):
		teacher_id = self.cleaned_data['teacher_id']
		subject_code = self.cleaned_data['subject_code']
		batch_num = self.cleaned_data['batch_num']
		semester = self.cleaned_data['semester']
		query = """SELECT * FROM teaches
					WHERE teacher_id='%s' AND subject_code='%s' AND batch_num='%s' AND semester='%s';
				"""%(teacher_id, subject_code, batch_num, semester)
		result, error = run_query(query, get_result=True)

		if len(result) > 1:
			raise forms.ValidationError('Record with teacher_id ' + teacher_id + ', subject_code ' + subject_code + 
										', batch_num ' + batch_num + ' and semester ' + semester + ' already exists')


class choosesForm(forms.Form):
	roll_no = forms.ChoiceField(choices=roll_no_fields(), label='Student')
	subject_code = forms.ChoiceField(choices=subject_code_fields(), label='Subject')
	semester = forms.ChoiceField(choices=semester_fields())

	def __init__(self, *args, **kwargs):
		super(choosesForm, self).__init__(*args, **kwargs)
		self.fields['roll_no'].choices = roll_no_fields()
		self.fields['subject_code'].choices = subject_code_fields()
		self.fields['semester'].choices = semester_fields()

	def clean_semester(self):
		semester = self.cleaned_data['semester']
		if semester not in ('1','2','3','4'):
			raise forms.ValidationError("Semester should be either 1, 2, 3 or 4")

		return semester

	def clean(self):
		roll_no = self.cleaned_data['roll_no']
		subject_code = self.cleaned_data['subject_code']
		semester = self.cleaned_data['semester']
		query = """SELECT * FROM chooses
					WHERE roll_no='%s' AND subject_code='%s' AND semester='%s';
				"""%(roll_no, subject_code, semester)
		result, error = run_query(query, get_result=True)

		if len(result) > 1:
			raise forms.ValidationError('Record with roll_no ' + roll_no + ' and subject_code ' + subject_code + ' already exists')

		query = """SELECT batch_num FROM belongs_to
					WHERE roll_no='%s';
				"""%(roll_no)
		result, error = run_query(query, get_result=True)

		if len(result) == 1:
			raise forms.ValidationError("Entry for the student with roll_no " + roll_no + " does not exist in table belongs_to")

		batch = result[1][0]

		query = """SELECT * FROM teaches
					WHERE subject_code='%s' AND batch_num='%s' AND semester='%s';
				"""%(subject_code, batch, semester)
		result, error = run_query(query, get_result=True)

		if error:
			raise forms.ValidationError(error)

		if len(result) == 1:
			raise forms.ValidationError("Entry for subject code %s in batch %s semester %s does not exist in table teaches"%(subject_code, batch, semester))


class studentUpdateForm(forms.Form):
	identifier = forms.IntegerField()
	roll_no = forms.CharField(label='Roll No')
	first_name = forms.CharField(max_length=20, label='First Name')
	middle_name = forms.CharField(max_length=20, required=False, label='Middle Name')
	last_name = forms.CharField(max_length=20, label='Last Name')

	def clean_roll_no(self):
		roll_no = self.cleaned_data['roll_no']

		try:
			split_txt = roll_no.split('/')
			t1 = split_txt[0].isdigit() and len(split_txt[0])==3
			t2 = str.isalpha(split_txt[1]) and len(split_txt[1])==4
			t3 = split_txt[2].isdigit() and (len(split_txt[2])==3)
			
			if not (t1 and t2 and t3):
				raise forms.ValidationError("Mismatch format for roll_no. Example: 072/MSCS/111")

			roll_no = split_txt[0] + '/' + split_txt[1].upper() + '/' + split_txt[2]

		except Exception as e:
			raise forms.ValidationError("Mismatch format for roll_no. Example: 072/MSCS/111")

		return roll_no


class subjectUpdateForm(forms.Form):
	identifier = forms.IntegerField()
	subject_code = forms.CharField(max_length=12, label='Subject')
	name = forms.CharField(max_length=100 )
	is_offered = forms.BooleanField(label='Is Offered')


class batchUpdateForm(forms.Form):
	identifier = forms.IntegerField()
	batch_num = forms.CharField(max_length=3, label='Batch')


class teacherUpdateForm(forms.Form):
	identifier = forms.IntegerField()
	teacher_id = forms.CharField(max_length=12)
	first_name = forms.CharField(max_length=20, label='First Name')
	middle_name = forms.CharField(max_length=20, required=False, label='Middle Name')
	last_name = forms.CharField(max_length=20, label='Last Name')


class belongs_toUpdateForm(belongs_toForm):
	identifier = forms.IntegerField()


class teachesUpdateForm(teachesForm):
	identifier = forms.IntegerField()


class choosesUpdateForm(choosesForm):
	identifier = forms.IntegerField()

class csvUpload(forms.Form):
	csv = forms.FileField(label='Upload CSV')