from configparser import ConfigParser


def configure(filename, section):
    parser = ConfigParser()
    parser.read(filename)
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db


def configflask(filename='Config/flask.ini', section='flask'):
    return configure(filename, section)


def configsql(filename='Config/sql.ini', section='sql'):
    return configure(filename, section)


def spotifyAuthParams(filename='Config/spotify.ini', section='spotify'):
    return configure(filename, section)