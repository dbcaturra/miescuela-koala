#run from: python manage.py shell
from django.contrib.auth.models import User
import pandas as pd
s = pd.read_csv("students.csv")
for i in s.values:
	#print(i[0],i[1])
	user=User.objects.create_user(i[0],password=i[1])
	user.is_superuser=False
	user.is_staff=False
	user.save()