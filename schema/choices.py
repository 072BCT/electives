from .run_raw_sql import run_query

def roll_no_fields():
	query = "SELECT roll_no, first_name ||' '|| middle_name ||' '|| last_name  FROM student;"
	result, _ = run_query(query, get_result=True)

	roll_num = []

	for entry in result[1:]:
		roll_num.append((entry[0], entry[1]+' ('+entry[0]+')'))

	return tuple(roll_num)


def batch_num_fields():
	query = "SELECT batch_num FROM batch order by batch_num;"
	result, _ = run_query(query, get_result=True)

	batch_num=[]

	for entry in result[1:]:
		batch_num.append((*entry, *entry))

	return tuple(batch_num)


def teacher_id_fields():
	query = "SELECT teacher_id, first_name ||' '|| middle_name ||' '|| last_name FROM teacher;"
	result, _ = run_query(query, get_result=True)

	teacher_id=[]

	for entry in result[1:]:
		teacher_id.append((entry[0], entry[1]+' ('+entry[0]+')'))

	return tuple(teacher_id)


def subject_code_fields():
	query = "SELECT subject_code, name FROM subject;"
	result, _ = run_query(query, get_result=True)

	subject_code=[]

	for entry in result[1:]:
		subject_code.append((entry[0], entry[1]+' ('+entry[0]+')'))

	return tuple(subject_code)


def semester_fields():
	return ((1,1), (2,2), (3,3), (4,4))