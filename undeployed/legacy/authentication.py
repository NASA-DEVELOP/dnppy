
import urllib
import urllib2
import cookielib

# target login url
auth_url = r"https://earthexplorer.usgs.gov/login/"
file_url = r"http://earthexplorer.usgs.gov/download/3372/LE70410362003114EDC00/STANDARD"
save_path = r"C:/test.html"

username = ""
password = ""

# store cookies and make an oppener to store them
cj                  = cookielib.CookieJar()
opener              = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
opener.addheaders   = [("user-agent", "Testing")]

#install opener
urllib2.install_opener(opener)

# password payload for sending
payload = {
    'op': 'login-main',
    'username': username,
    'password': password
    }

# encode the payload
data = urllib.urlencode(payload)

# build a request object
req  = urllib2.Request(auth_url, data)
resp = urllib2.urlopen(req)

contents = resp.read()
