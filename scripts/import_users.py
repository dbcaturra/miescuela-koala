#run from: python manage.py shell
import pandas as pd
s = pd.read_csv("scripts/students.csv")
for i in s.values:
	#print(i[0],i[1])
	user=Person.objects.create_user(i[0],password=i[1])
	user.is_superuser=False
	user.is_staff=False
	user.save()
