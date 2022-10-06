from tabulate import tabulate
import pandas as pd
from tabulate import tabulate


student = {
    "student1": {
        "Name": "Eddy",
        "Grade": 1,
        "Math": 78,
        "English": 65,
        "Physics": 89,
        "Chemistry": 80,
        "tes1t": 11
    },
    # "student2": {
    #     "Name": "Jim",
    #     "Grade": 2,
    #     "Math": 89,
    #     "English": 65,
    #     "Physics": 87,
    #     "Chemistry": 76,
    #    # "test": 22

    # },
    # "student3": {
    #     "Name": "Jane",
    #     "Grade": 3,
    #     "Math": 87,
    #     "English": 97,
    #     "Physics": 75,
    #     "Chemistry": 64,
    #    # "test": 33

    # },
}

# df = pd.DataFrame(student.values())
# print(tabulate(df, headers='keys', tablefmt='psql'))

headers = ["student", "Name", "Grade", "Math", "English", "Physics", "Chemistry","test"]
df = pd.DataFrame(student).T
print(tabulate(df, headers=headers, tablefmt='psql'))

#df = pd.DataFrame(student).T
#print(tabulate(df, headers='keys', tablefmt='psql'))

