import sys, os
from make_log import log_exceptions

try:
    a = 1
    2+'a'
    if a != 2:
        sys.exit('exit ad aasdasd')
except SystemExit as e:
    v = e.code
    if 'exit' in v:
        a =1
        os._exit(0)
except:
    log_exceptions()