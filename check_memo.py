import uos

# get file system information
fs_stat = uos.statvfs('/')

# calculate the amount of free space in bytes
free_space = fs_stat[0] * fs_stat[3]

# print the amount of free space in MB
print('Free space:', free_space / 1024 / 1024, 'MB')
