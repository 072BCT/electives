from django.db import models

class student(models.Model):
	roll_no = models.CharField(max_length=12, primary_key=True)
	first_name = models.CharField(max_length=20)
	middle_name = models.CharField(max_length=20, blank=True, null=True)
	last_name = models.CharField(max_length=20)

	# def __str__(self):
	# 	return self.roll_no

	class Meta:
		db_table = 'student'
		verbose_name_plural='student'


class subject(models.Model):
	subject_code = models.CharField(max_length=12, primary_key=True)
	name = models.CharField(max_length=100)
	is_offered = models.BooleanField(default=0)

	# def __str__(self):
	# 	return self.subject_code

	class Meta:
		db_table = 'subject'
		verbose_name_plural='subject'


class batch(models.Model):
	batch_num = models.CharField(max_length=3, primary_key=True)

	# def __str__(self):
	# 	return self.batch_num

	class Meta:
		db_table = 'batch'
		verbose_name_plural='batch'

class teacher(models.Model):
	teacher_id = models.CharField(max_length=12, primary_key=True)
	first_name = models.CharField(max_length=20)
	middle_name = models.CharField(max_length=20, blank=True, null=True)
	last_name = models.CharField(max_length=20)

	# def __str__(self):
	# 	return self.teacher_id

	class Meta:
		db_table = 'teacher'
		verbose_name_plural='teacher'

class chooses(models.Model):
	roll_no = models.ForeignKey(student, db_column='roll_no', on_delete=models.CASCADE)
	subject_code = models.ForeignKey(subject, db_column='subject_code', on_delete=models.CASCADE)
	semester = models.CharField(max_length=1)

	class Meta:
		db_table = 'chooses'
		verbose_name_plural='chooses'

class teaches(models.Model):
	teacher_id = models.ForeignKey(teacher, db_column='teacher_id', on_delete=models.CASCADE)
	batch_num = models.ForeignKey(batch, db_column='batch_num', on_delete=models.CASCADE)
	subject_code = models.ForeignKey(subject, db_column='subject_code' ,on_delete=models.CASCADE)
	semester = models.CharField(max_length=1)

	class Meta:
		db_table = 'teaches'
		verbose_name_plural = 'teaches'

class belongs_to(models.Model):
	roll_no = models.ForeignKey(student, db_column='roll_no', on_delete=models.CASCADE)
	batch_num = models.ForeignKey(batch, db_column='batch_num', on_delete=models.CASCADE)

	# def __str__(self):
	# 	return self.roll_no

	class Meta:
		db_table = 'belongs_to'
		verbose_name_plural = 'belongs_to'
