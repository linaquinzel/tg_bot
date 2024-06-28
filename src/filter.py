import re

line = "00-50:B6:5B:CA:6A"

def mac_address_check(string):
    t = re.findall (r'[0-9a-fA-F]+', string)
    if len(t)!=6 or len(string)!=17:
        return False
    for i in t:
        if not re.match('[0-9a-fA-F]+', i):
            return False
    return True

def unsubscribe_check(string):
    t = string.split()
    if t[0] == 'unsubscribe' and mac_address_check(t[1]):
        return True
    return False
    

    



        