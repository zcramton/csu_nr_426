>>> species = "marmota monax"
>>> x = species.split(" ")
>>> print x
['marmota', 'monax']
>>> genus = x[0]
>>> genus2 = genus[:1}
SyntaxError: invalid syntax
>>> genus2 = genus[:1]
>>> print genus2
m
>>> genus2 = genus[:2]
>>> print genus2
ma
>>> genus3 = x[0][:2]
>>> print genus3
ma
>>> abbrev = x[0][:2]+x[1][:2]
>>> print abbrev
mamo
>>> ABBREV = x[0][:2]+x[1][:2].upper()
>>> print ABBREV
maMO
>>> ABBREV = x[0][:2].upper() + x[1][:2].upper()
>>> print ABBREV
MAMO
>>> 
