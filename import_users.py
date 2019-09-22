#run from: python manage.py shell
import pandas as pd
s = pd.read_csv("students.csv")
for i in s.values:
	#print(i[0],i[1])
	
