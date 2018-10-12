#coding=utf8

import requests

host = 'http://127.0.0.1:6666'
s = requests.Session()

#r = s.get(host+'/createuser')
#print r.content

r0 = s.get(host+'/login')
print r0.content

r2 = s.get(host+'/createpost')
print r2.content



r0 = s.get(host+'/login2')
print r0.content

r2 = s.get(host+'/createpost2')
print r2.content