import json

from sources.OpenData.DadesObertes.CEEE.datasource import CEEEDataSource

if __name__ == '__main__':
    with open("config.json") as config_f:
        config = json.load(config_f)

    source = CEEEDataSource(config)
    source.gather()
