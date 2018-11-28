from django.shortcuts import render
from django.http.response import HttpResponseRedirect
from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login as contrib_login
from django.views.decorators.csrf import csrf_exempt

from .forms import *
from .run_raw_sql import run_query
#from .sql_views import *

#model, table, relation all mean the same thing
#dictionary containing all the models in 'schema' app
all_models = dict(apps.all_models['schema'])

id_map = {}	#map id number with the specific record in a model
#format: {id_number : [modelName, {PK_field: PK_value}]}
curr_id = 0

def increase_id_value():
	global curr_id
	if(curr_id > 99999):
		curr_id = 0
	curr_id+=1

def get_pk_field(modelName):
	query = """	SELECT a.attname
				FROM   pg_index i
				JOIN   pg_attribute a ON a.attrelid = i.indrelid
                AND a.attnum = ANY(i.indkey)
				WHERE  i.indrelid = '%s'::regclass
				AND    i.indisprimary;
			"""%(modelName)
	result, error = run_query(query, get_result=True)
	return result[1][0]


def get_fk_field(modelName):
	query = """
			SELECT
    		ccu.column_name AS foreign_column_name 
			FROM 
		    information_schema.table_constraints AS tc 
		    JOIN information_schema.key_column_usage AS kcu
		    ON tc.constraint_name = kcu.constraint_name
		    AND tc.table_schema = kcu.table_schema
		   	JOIN information_schema.constraint_column_usage AS ccu
		    ON ccu.constraint_name = tc.constraint_name
		    AND ccu.table_schema = tc.table_schema
			WHERE constraint_type = 'FOREIGN KEY' AND tc.table_name='%s';
			"""%(modelName)
	result, error = run_query(query, get_result=True)
	
	if len(result) == 1:	#No FK Fields
		return None

	result = result[1:]
	result = [column_name for tup in result for column_name in tup]
	return result


def get_all_fields(modelName):
	query = """
			SELECT * FROM %s
			WHERE false;
			"""%(modelName)

	result, error = run_query(query, get_result=True)
	return result[0]


def not_key_fields(modelName):
	pk_field = [get_pk_field(modelName)]
	fk_field = get_fk_field(modelName)
	all_fields = get_all_fields(modelName)

	nkFields = []
	for field in all_fields:
		t1 = field not in pk_field
		t2 = field not in fk_field
		t3 = field != 'id'

		if t1 and t2 and t3:
			nkFields.append(field)

	return nkFields


def update_record(modelName, field, val, data):
	updates = ''
	for col in data:
		updates += col + "='" + str(data[col]) + "',"
	updates = updates[:-1]
	statement = """UPDATE %s
					SET %s
					WHERE %s='%s';
				"""%(modelName, updates, field, val)
	error = run_query(statement)
	return error


def login(request):
	if request.user.is_authenticated:
		return HttpResponseRedirect('/relations/')

	return contrib_login(request)


@login_required(login_url='login')
def sql_query(request):
	result = error = query = None
	if request.method == 'POST':
		form = QueryForm(request.POST)

		if form.is_valid():
			form_data = form.cleaned_data
			query = form_data['query']
			result, error = run_query(query, get_result=True)
			print(result)
			print(error)

	form = QueryForm(initial = {'query': query})
	return render(request, 'sql_query.html', {'form': form, 'result':result, 'error':error})


def create_student_record(request, form):
	cols = vals = ''
	error = result = None
	if form.is_valid():
		data = form.cleaned_data
		print(data)
		for key in data:
			if key == 'batch':
				continue
			if data[key] is None:
				data[key] = ''

			cols += key + ","
			vals += "'" + str(data[key]) + "',"
			#col_val += key + "='" + data[key] + "',"
		
		cols = cols[:-1]
		vals = vals[:-1]

		statement = """INSERT INTO student (%s)
						VALUES (%s);
					"""%(cols, vals)

		error1 = run_query(statement)

		if error1:
			error = 'Could not insert record: ' + error1 + '\n'

		statement = """
					INSERT INTO belongs_to(batch_num, roll_no)
					VALUES ('%s', '%s');
					"""%(data['batch'], data['roll_no'])

		print(statement)
		error1 = run_query(statement)

		if error1:
			print(error1)
			error = str(error) + error1 + '\n'

		if error:
			result = error
		else:
			result = 'Insertion successful'
		
	return render(request, 'create_record.html', {'form': form, 'message': result, 'modelName': 'student'})
	

@login_required(login_url='login')
def create_record(request, modelName):
	error = result = None

	if modelName not in all_models:
		error = "Table '" + modelName + "' does not exist"
		return list_relations(request, error=error)
	
	formName = modelName + 'Form'
	formClass = globals()[formName]

	if request.method == 'POST':

		cols = vals = ''
		form = formClass(request.POST)

		if modelName == 'student':
			return create_student_record(request, form)
		else:
			error = 'Invalid data'	#assume input data to be invalid until checked in the next if statement
			if form.is_valid():
				data = form.cleaned_data
				for key in data:
					if data[key] is None:
						data[key] = ''

					cols += key + ","
					vals += "'" + str(data[key]) + "',"
					#col_val += key + "='" + data[key] + "',"
				
				cols = cols[:-1]
				vals = vals[:-1]

				statement = """INSERT INTO %s (%s)
								VALUES (%s);
							"""%(modelName, cols, vals)

				error = run_query(statement)

				if error:
					result = 'Could not insert record: ' + error
				else:
					result = 'Insertion successful'

	else:
		form = formClass()

	return render(request, 'create_record.html', {'form': form, 'message': result, 'modelName': modelName})


@login_required(login_url='login')
def list_relations(request, error=None):
#lists all the tables in database
	models = []
	for model in all_models:
		models += [model]

	models.sort()
	return render(request, 'relations.html', {'models': models, 'error': error})


@login_required(login_url='login')
def edit_record(request, modelName, recordNum):
	global curr_id
	error = result = form = None
	recordNum -= 2

	if modelName in all_models:
		formName = modelName + 'UpdateForm'
		formClass = globals()[formName]
		
		if request.method == 'POST':
			form = formClass(request.POST)
			if form.is_valid():
				data = form.cleaned_data
				identifier = data['identifier']
				data.pop('identifier')
				if identifier in id_map:
					entry = id_map[identifier]
					entry_model = entry[0]
					field_val = entry[1]
					field = list(field_val.keys())[0]
					val = field_val[field]
					error = update_record(entry_model, field, val, data)

					if not error:
						return HttpResponseRedirect('/relations/' + modelName + '/')

		else:
			if recordNum < 0:
				error = 'Invalid request'
				return HttpResponseRedirect('/relations/' + modelName)

			else:
				query = "SELECT * FROM " + modelName + " LIMIT 1 OFFSET " + str(recordNum)
				result, error = run_query(query, get_result=True)
				
				if not error:

					key_val = {key:val for key,val in zip(result[0],result[1])}

					pkField = get_pk_field(modelName)
					pkValue = key_val[pkField]
					increase_id_value()	#get new value of curr_id and set to 0 if necessary

					map_entry = {curr_id : [modelName, {pkField: pkValue}]}
					id_map.update(map_entry)			
					key_val.update({'identifier': curr_id})
					form = formClass(initial=key_val)

	else:
		error = "Table '" + modelName + "' does not exist"
		return list_relations(request, error=error)

	form.fields['identifier'].widget = forms.HiddenInput()
	return render(request, 'edit_record.html', {'form':form, 'error': error})


@login_required(login_url='login')
def delete_record(request, modelName, recordNum):
	recordNum -= 2 
	if modelName not in all_models:
		error = "Table '" + modelName + "' does not exist"
		return list_relations(request, error=error)

	query = "SELECT * FROM " + modelName + " LIMIT 1 OFFSET " + str(recordNum)
	result, error = run_query(query, get_result=True)

	if error:
		return render(request, 'list_relations.html', {'error': error})

	key_val = {key:val for key,val in zip(result[0],result[1])}

	condition = ""
	for key in key_val:
		if key_val[key] == '' or key_val[key] == None:
			continue

		condition += str(key) + "='" + str(key_val[key]) + "' AND "

	condition = condition[:-4]
	statement = """DELETE FROM %s
					WHERE %s;
				"""%(modelName, condition)

	error = run_query(statement)

	if error:
		error = "Cannot delete from " + modelName + ": " + str(error)
		return list_relations(request, error=error)

	return HttpResponseRedirect('/relations/'+modelName)


def get_fk(fk_table, table):
	for fk in fk_table:
		if fk_table[fk] == table:
			return fk


# @csrf_exempt
# @login_required(login_url='login')
# def table_data(request, modelName):
# 		fk_table = {
# 		'roll_no': 'student',
# 		'teacher_id': 'teacher',
# 		'subject_code': 'subject',
# 		'batch_num': 'batch'
# 	}

# 	table_alt_field = {
# 		'student': ['student_name', 'roll_no', 'first_name', 'middle_name', 'last_name'],
# 		'teacher': ['teacher_name', 'teacher_id','first_name', 'middle_name', 'last_name'],
# 		'subject': ['subject', 'subject_code', 'name'],
# 		'batch': ['batch', 'batch_num']

# 	}

# 	if modelName not in all_models:
# 		error = "Table '" + modelName + "' does not exist"
# 		return list_relations(request, error=error)

# 	fk_fields = get_fk_field(modelName)
# 	referenced_tables = [modelName]
# 	result = None

# 	if fk_fields:
# 		other_fields = not_key_fields(modelName)
# 		[referenced_tables.append(fk_table[fk]) for fk in fk_fields]
# 		fields = ', '.join(fk_fields) + ', '

# 		for table in referenced_tables[1:]:   #excluding modelName which is referenced_tables[0]
# 			alt_field = table_alt_field[table]
# 			fk = get_fk(fk_table, table)
						
# 			field = "||' '||".join(alt_field[2:])

# 			if field is not '': 
# 				fields += field + ' AS %s, '%(alt_field[0])

# 		fields = fields[:-2] + ', '
# 		fields += ', '.join(other_fields)

# 		if fields[-2] == ',':
# 			fields=fields[:-2]

# 		table_names += ' NATURAL JOIN '.join(referenced_tables)
		
# 		query = """
# 				SELECT %s
# 				FROM %s;
# 				"""%(fields, table_names)

# 	if fk_fields:
# 		other_fields = not_key_fields(modelName)

# 		[referenced_tables.append(fk_table[fk]) for fk in fk_fields]
# 		fields=""
# 		table_names = ""

# 		fields = ', '.join(fk_fields) + ', '
# 		for table in referenced_tables[1:]:   #excluding modelName which is referenced_tables[0]
# 			alt_field = table_alt_field[table]
# 			fk = get_fk(fk_table, table)
						
# 			field = "||' '||".join(alt_field[2:])

# 			if field is not '': 
# 				fields += field + ' AS %s, '%(alt_field[0])

# 		fields = fields[:-2] + ', '
# 		fields += ', '.join(other_fields)

# 		if fields[-2] == ',':
# 			fields=fields[:-2]

# 		table_names += ' NATURAL JOIN '.join(referenced_tables)
		
# 		query = """
# 				SELECT %s
# 				FROM %s;
# 				"""%(fields, table_names)


# 		temp, error = run_query(query, get_result=True)

# 		ind = []
# 		i=0


# 		for f in temp[0]:
# 			if f in alt_field_req or f not in all_alt_fields:
# 				ind.append(i)

# 			if f in fk_fields:
# 				table = fk_table[f]
# 				alt_fields = table_alt_field[table]

# 				if f == 'batch_num':
# 					options.append(['batch_num'])
# 				else:
# 				 	options.append([f, alt_fields[0]])

# 			i += 1
# 		#print(temp[0])

# 		result = []
# 		for row in temp:
# 			i = 0
# 			t = []
# 			for data in row:
# 				if i in ind:
# 					t.append(data)
# 				i+=1
# 			result.append(t)

# 		temp_option = []

# 		for f in result[0]:
# 			for t in options[1:]:
# 				if f in t:
# 					temp_option.append(t)

# 		options = [None] + temp_option 



# 	else:
# 		query = """
# 				SELECT * FROM %s
# 				"""%(modelName)
# 		result, error = run_query(query, get_result=True)



@csrf_exempt
@login_required(login_url='login')
def table_data(request, modelName):
	fk_table = {
		'roll_no': 'student',
		'teacher_id': 'teacher',
		'subject_code': 'subject',
		'batch_num': 'batch'
	}

	table_alt_field = {
		'student': ['student', 'roll_no', 'first_name', 'middle_name', 'last_name'],
		'teacher': ['teacher', 'teacher_id','first_name', 'middle_name', 'last_name'],
		'subject': ['subject', 'subject_code', 'name'],
		'batch': ['batch', 'batch_num']
	}
	if modelName not in all_models:
		error = "Table '" + modelName + "' does not exist"
		return list_relations(request, error=error)

	if modelName == 'student':
		if request.method == 'POST':
			if 'csv' in request.FILES:
				csv = request.FILES['csv']

				batch_ind = None
				roll_no_ind = None
				batch_list = []
				
				records = []

				header = csv.readline().decode('UTF-8')
				header = header[:-1].split(',')
				print(header)
				if str('batch') in header:
					batch_ind = header.index('batch')
					roll_no_ind = header.index('roll_no')

				for line in csv:
					line = line[:-1].decode('UTF-8')
					line = line.split(',')

					if batch_ind:
						try:
							line.remove('batch')
						except:
							batch_list.append(line[batch_ind])
							del line[batch_ind]


					line = ["'"+l+"'" for l in line]
					records.append(line)


				for record in records[1:]:
					query = """
							INSERT INTO student (%s)
							VALUES (%s);
							"""%(','.join(records[0]),
								 ','.join(record))

					print(query)

				for record,batch in zip(records[1:],batch_list):
					query = """
							INSERT INTO belongs_to ('roll_no', 'batch_num')
							VALUES ('%s', '%s');
							"""%(record[roll_no_ind], batch)

					print(query)
					
	referenced_tables = [modelName]
	options = None
	result = None

	all_alt_fields = [field for l in table_alt_field for field in table_alt_field[l][:2]]

	fk_fields = get_fk_field(modelName)
	
	alt_field_req = fk_fields

	if fk_fields:
		other_fields = not_key_fields(modelName)
		options = [None]
		[referenced_tables.append(fk_table[fk]) for fk in fk_fields]
		fields=""
		table_names = ""

		fields = ', '.join(fk_fields) + ', '
		for table in referenced_tables[1:]:   #excluding modelName which is referenced_tables[0]
			alt_field = table_alt_field[table]
			fk = get_fk(fk_table, table)
						
			field = "||' '||".join(alt_field[2:])

			if field is not '': 
				fields += field + ' AS %s, '%(alt_field[0])

		fields = fields[:-2] + ', '
		fields += ', '.join(other_fields)

		if fields[-2] == ',':
			fields=fields[:-2]

		table_names += ' NATURAL JOIN '.join(referenced_tables)
		
		query = """
				SELECT %s
				FROM %s;
				"""%(fields, table_names)


		temp, error = run_query(query, get_result=True)

		header = []
		merge_list = []

		for f_ind,f in enumerate(temp[0]):
			if f in fk_table:
				header.append(table_alt_field[fk_table[f]][0])
				for i, merge_field in enumerate(temp[0][f_ind:]):
					if f != merge_field and merge_field in table_alt_field[fk_table[f]]:
						merge_list.append([f_ind, f_ind + i])
				# for i,merge_field in enumerate(temp[0]):
				# 	if merge_field != f and merge_field in table_alt_field[fk_table[f]]	[1:]:
				# 		merge_list.append([f_ind, i])
			elif f in other_fields:
				header.append(f)

		result = [header]
		for row in temp[1:]:
			remove_entries = []
			row = list(row)
			for merge_ind in merge_list:
				remove_entries.append(row[merge_ind[1]])
				row[merge_ind[0]] = row[merge_ind[1]] + ' (' + row[merge_ind[0]] + ')'

			for entry in remove_entries:
				row.remove(entry)

			result.append(row)

		if request.method == 'POST':
			formData = dict(request.POST)
			print(formData)

			if modelName == 'chooses':
				filterVal = formData['studentName'][0]
			elif modelName == 'teaches':
				filterVal = formData['teacherName'][0]

			for record in result[1:]:
				print([record[0][:len(filterVal)].lower(), filterVal.lower()])
				if record[0][:len(filterVal)].lower() != filterVal.lower():
					result.remove(record)



		# temp_option = []

		# for f in result[0]:
		# 	for t in options[1:]:
		# 		if f in t:
		# 			temp_option.append(t)

		# options = [None] + temp_option


	else:
		query = """
				SELECT * FROM %s
				"""%(modelName)
		result, error = run_query(query, get_result=True)

	return render(request, 'table_data.html', {'modelName': modelName, 'result': result})