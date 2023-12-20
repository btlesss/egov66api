# egov66api
Python api wrapper for [dnevnik.egov66.ru](https://dnevnik.egov66.ru)

### Example of usage
```python
from dnevnikapi import Dnevnik, types
import pickle

with Dnevnik("Login","Password", auto_logout=False) as cl:
	au = cl.auth_data
	#save auth data to file/database as binary data
	with open("account.data", "wb") as f:
		f.write(pickle.dumps(au))

#previous session usage
with Dnevnik(auth_data=au) as cl:
	# by default first available student selected as current,
	# but you can change it
	if len(cl.available_students) > 1:
		print(*cl.available_students, sep="\n")
		num = int(input("select: "))
		cl.student = cl.available_students[num]
	
	# call some methods
	period = cl.get_estimate_periods()[0]
	print(cl.get_estimate(period))
```