# This is what I use for python source documentation. I don't use pydoc... this is easier for me.

files = [XXX] # fill in the files you want to outline
outfile = '_outline.py' # for syntax highlighting i left the py extension in
outlines = []

for f in files:
	file = open(f, 'r')
	states = ['just_saw_def', 'just_saw_class', 'comment_started', 'just_saw_decorator']
	state = None
	for line in file:
		line = line.rstrip('\n')
		if line.strip().startswith('def '):
			if state != 'just_saw_decorator':
				outlines.append('')
			outlines.append(line)
			state = 'just_saw_def'
		elif line.strip().startswith('class '):
			outlines.append('')
			outlines.append(line)
			state = 'just_saw_class'
		elif line.strip().startswith('"""'):
			if state == 'comment_started' and line.strip() == '"""':
				outlines.append(line)
				state = None
			elif state in ['just_saw_def', 'just_saw_class']:
				outlines.append(line)
				state = 'comment_started'
				if line.strip().endswith('"""') and line.strip() != '"""':
					state = None
		else:
			if state == 'comment_started':
				outlines.append(line)
				if line.strip().endswith('"""'):
					state = None
			elif line.strip().startswith('@'):
				outlines.append('')
				outlines.append(line)
				state = 'just_saw_decorator'

outfile = open(outfile, 'w')
outfile.write("\n".join(outlines))

