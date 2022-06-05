from os import path
import sys

# The very initial message
print('More information at https://github.com/Nyanm/Saccharomyces-cerevisiae')

TEST_MODE = 1
# Turn off test mode when packing the program
if TEST_MODE:
    local_dir = '/'.join(path.dirname(path.abspath(__file__)).replace('\\', '/').split('/')[:-1])
else:
    local_dir = path.dirname(path.abspath(sys.executable)).replace('\\', '/')
