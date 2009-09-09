import ConfigParser

_config = ConfigParser.SafeConfigParser()

def readConfig(file):
    _config.read(file)

def parameter(section, option):
    return _config.get(section, option)
