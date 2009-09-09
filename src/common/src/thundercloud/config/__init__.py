import simplejson as json

def readConfigFromFile(file):
    f = open(file, "r")
    jsonRepresentation = json.loads(f.read())
    for attr in jsonRepresentation:
        pass


MASTER_PORT = 6000
SLAVE_PORT = 7000
CLIENT_UPPER_BOUND = 1000