from schema.models import student, teacher, subject

teacher_id_base = 'PUL10'
teacher_counter = 0
subject_code_base = 'MSCS00'
subject_counter = 0

with open('./electives2.csv') as csv:
	for line in csv:		
		if line == '\n':
			continue
		try:
			subject_teacher = line.split('(')
			subject_name = subject_teacher[0].rstrip()
			teacher_name = subject_teacher[1].split(')')[0].rstrip()
			
			teacher_name = teacher_name.split(' ')
			middle_name = ''
			first_name = teacher_name[0]
			last_name = teacher_name[1]

			if len(teacher_name) == 3:
				middle_name = teacher_name[1]
				last_name = teacher_name[2]

			teacher_id = teacher_id_base + str(teacher_counter)
			teacher_counter += 1

			try:
				teacher.objects.create(first_name=first_name, middle_name=middle_name, last_name=last_name, teacher_id=teacher_id)
			except:
				pass

			subject_code = subject_code_base + str(subject_counter)
			subject_counter += 1

			
			try:
				subject.objects.create(subject_code=subject_code, name=subject_name)
			except:
				pass

		except:
			student_info = line.split(',')
			roll_num = student_info[1]
			student_name = student_info[2].rstrip()
			
			student_name = student_name.split(' ')
			middle_name = ''
			first_name = student_name[0]
			last_name = student_name[1]
			if len(student_name) == 3:
				middle_name = student_name[1]
				last_name = student_name[2]
			try:
				student.objects.create(first_name=first_name, middle_name=middle_name, last_name=last_name, roll_no=roll_num)
			except:
				pass