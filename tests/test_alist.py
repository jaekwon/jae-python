from utils import alist

a = alist()
a['foo'] = 'bar'
assert a == [('foo', 'bar')]

a = alist()
a['foo'] = 'bar'
a[1] = 2
a['bar'] = 'baz'
assert a == [('foo', 'bar'), (1, 2), ('bar', 'baz')]

# when you overwrite...
a['foo'] = 'zap'
assert a == [(1,2), ('bar', 'baz'), ('foo', 'zap')]

a = alist()
a.append( 'foo', 'bar' )
a.append( 1, 2 )
a.append( 'bar', 'baz' )
assert a == [('foo', 'bar'), (1,2), ('bar', 'baz')]

b = alist()
b.extend( a )
assert a == b

c = alist(a)

assert a == b and b == c
