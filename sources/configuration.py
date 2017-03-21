import json

def getConfiguration():
    configuration = None

    with open('../configuration.json') as data_file:
        configuration = json.load(data_file)

    if ("subreddits" not in configuration.keys() or not configuration["subreddits"]):
        raise ValueError("Configuration.json has to contain a list of subreddits under the key 'subreddits'.")

    setMissingValues(configuration) # defaults for database and reddit configuration

    return configuration

def setMissingValues(configuration):
    configuration["database"] = configuration.get("database", {"host": "localhost", "port": 27017})
    configuration["database"]["host"] = configuration["database"].get("host", "localhost")
    configuration["database"]["port"] = configuration["database"].get("port", 27017)

    configuration["reddit"] = configuration.get("reddit", {"client_id": "FM_44Hgx49pC7g",
                                                           "client_secret": "GxfbBqDjgntCEl176uJakmEr_p4",
                                                           "user_agent": "hootsuite_bot:v1.0"})
    configuration["reddit"]["client_id"] = configuration["reddit"].get("client_id", "FM_44Hgx49pC7g")
    configuration["reddit"]["client_secret"] = configuration["reddit"].get("client_secret", "GxfbBqDjgntCEl176uJakmEr_p4")
    configuration["reddit"]["user_agent"] = configuration["reddit"].get("user_agent", "hootsuite_bot:v1.0")

    configuration["webserver"] = configuration.get("webserver", {"host": "localhost", "port": 5000})
    configuration["webserver"]["host"] = configuration["webserver"].get("host", "localhost")
    configuration["webserver"]["port"] = configuration["webserver"].get("port", 5000)
