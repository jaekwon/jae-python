import datetime

def timeago(timestamp):
	""" returns:
		- x minutes ago
		- x hours ago
		- x/y/z
	"""
	now = int(datetime.datetime.utcnow().strftime('%s'))
	diff = now - timestamp
	dt = datetime.datetime.fromtimestamp(timestamp)
	
	# strange case where timestamp is in the future... just show the date
	if diff < 0:
		return "%s/%s/%s" % (dt.month, dt.day, str(dt.year)[2:])
	elif diff < 60*60: # less than an hour ago
		return "%s minutes ago" % str(int(diff/60))
	elif diff < 60*60*24:
		return "%s hours ago" % str(int(diff/3600))
	else:
		return "%s/%s/%s" % (dt.month, dt.day, str(dt.year)[2:])
