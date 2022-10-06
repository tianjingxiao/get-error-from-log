# # Python implementation to
# # read last N lines of a file

# # Function to read
# # last N lines of the file
# # def LastNlines(fname):
# # 	with open(fname) as file:
# # 		content = (file.readlines() [-5:])
# # 		for line in content:
# # 			print(line, end ='')
# # 			if 'error' in content:
# # 				print(line, end ='')
# # 			else:
# # 				print('error does not exist')

# import re

# def escape_ansi(line):
#     ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
#     return ansi_escape.sub('', line)



# def check_flash_error(serial_number: str):
#     file = f"{serial_number}.log"
#     count = 0
#     with open(file) as file:
#         line = (file.readlines() [-10:])
#         #print(content)
#         for line in line:
#         	count += 1
#         #	print("Line{}: {}".format(count, line.strip()))
#         	if "Error" in line:
#         		newline = escape_ansi(line)
#         		print(f"\033[031m{newline}\033[0m")

#         	# print(line)
#         	# if 'error' in line:
#         	# 	print(line)
#         	# else:
#         	# 	print('error does not exist')	





# check_flash_error('0033002C3239510539303836copy')

# print("001\n")
# print("001\n")
# print("001\n")
# print("001\n")
# print("001\n")


from datetime import datetime

now = datetime.now()

current_time = now.strftime("%m/%d/%Y/%H:%M:%S")
print("Current Time =", current_time)