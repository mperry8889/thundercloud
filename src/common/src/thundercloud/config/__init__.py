import ConfigParser

_config = ConfigParser.SafeConfigParser()

def readConfig(file):
    _config.read(file)

def parameter(section, option, type=None):
    if type is bool:
        return _config.getboolean(section, option)
    elif type is int:
        return _config.getint(section, option)
    elif type is float:
        return _config.getfloat(section, option)
    else:
        return _config.get(section, option)

def section(section):
    return _config.items(section)