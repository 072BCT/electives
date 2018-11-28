from django.db import connection

def run_query(query, get_result=False):
	result = error = None
	with connection.cursor() as cursor:
		try:
			cursor.execute(query)
		except Exception as e:
			error = str(e)

		if not error and get_result:
			columns = [col[0] for col in cursor.description]
			result = cursor.fetchall()
			result = [columns] + result

	if get_result:
		return result, error

	return error