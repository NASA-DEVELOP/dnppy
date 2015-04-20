# try to get the requests module
try:
    import requests
except:
    print("you do not have the 'requests' module, download it here")
    print("https://pypi.python.org/pypi/requests/")

    

# print release statistics
releases    = requests.get("https://api.github.com/repos/nasa/dnppy/releases")
#releases    = requests.get("https://api.github.com/repos/scikit-learn/scikit-learn/releases")

for release in releases.json():
    print("dnppy release '{0}' with name '{1}' has assets:\n{2}".format(
                release["id"],release["name"],release["assets"]))
