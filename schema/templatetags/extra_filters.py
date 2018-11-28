from django import template

register = template.Library()

@register.filter
def get_by_index(l, i):
    return l[i]

@register.filter
def recordsCount(l):
	return len(l)-1

@register.filter
def isArray(l):
	if isinstance(l, list):
		return True

@register.filter
def absCount(num):
	return num-1
