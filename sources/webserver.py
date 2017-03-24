from flask import Flask, request, Response, json
import pymongo
import sys

from db_api_wrapper import DBWrapper
import configuration
from r2d2_errors import R2D2_BadValueError, R2D2_ConfigurationError, R2D2_DatabaseError

app = Flask(__name__)


@app.route('/items', methods = ['GET'])
def replyToQuery():
    global db_connection

    # Get the values of the parameters from the URL query string.
    subreddit = request.args.get("subreddit")
    t1 = request.args.get("t1")
    t2 = request.args.get("t2")
    kw = request.args.get("keyword")

    try:
        query = getQuery(subreddit, t1, t2, kw)

        cursor = db_connection.items.find(filter=query,
                               projection={"_id": 0}, # omit the default mongo id field
                               sort=[("timestamp", pymongo.DESCENDING)]) # sort in reverse chronological order

        # Read all the data into a list.
        data = list(cursor)
        response = Response(response=json.dumps(data),
                            status=200,
                            mimetype='application/json')

    except R2D2_BadValueError as e:
        msg = "An error occured: " + e.message + "<br/>"
        msg += "Query string should be similar to : /items?subreddit=&ltsubreddit&gt&from=&ltt1&gt&to=&ltt2&gt&keyword=&ltkw&gt <br/>"
        msg += "Parameters: <br/> subreddit is the name of a subredit e.g. learnpython"
        msg += "<br/> t1 and t2 defne the timeframe of the items: t1 &le; 'item time' &lt t2. They should be UNIX time stamps."
        msg += "<br/> keyword is a word to search for in the content of items. The search is case-insensitive."
        msg += "<br/><br/> keyword is optional, all other parameters are mandatory."

        response = Response(response=msg,
                           status=404)

    except Exception as e:
        msg = "An unexpected error occured: " + e.message

        response = Response(response=msg,
                           status=404)

    return response


def getQuery(subreddit, t1, t2, keyword):
    """Constructs the query to retrieve data from the DB."""
    if not subreddit or not t1 or not t2:
        raise R2D2_BadValueError("Parameters subreddit, t1 and t2 are mandatory.")

    try:
        t1 = float(t1)
        t2 = float(t2)
        if t1 < 0 or t2 < 0:
            raise ValueError("")

    except ValueError:
        raise R2D2_BadValueError("Parameters t1 and t2 should be non-negative real numbers.")

    query = {"subreddit": {"$eq": subreddit},
             "timestamp": {"$gte": t1, "$lt": t2}}

    # If keyword is present, perform a search for that keyword in the 'content' field of the collection.
    # The search uses the keywordIndex, it is case-insensitive and only look sofr exact matches.
    if keyword:
        query["$text"] = { "$search": keyword }

    return query


@app.route('/all')
def listAll():
    """Display the entire contents of the DB."""
    config = configuration.getConfiguration()
    db = DBWrapper(config["database"])

    cursor = db.items.find(filter={},
                           projection={"_id": 0, "content": 0},
                           sort=[("timestamp", pymongo.DESCENDING)])

    results = list(cursor)

    response = Response(response=json.dumps(results),
                        status=200,
                        mimetype='application/json')

    return response


if __name__ == '__main__':
    try:
        # Gets the configuration to use. These are settings regarding which port and host the server should use.
        server_config = configuration.getConfiguration()

        # Connect to the database.
        db_connection = DBWrapper(server_config["database"])

        app.run(
            host=server_config["webserver"]["host"],
            port=int(server_config["webserver"]["port"]))

    except R2D2_ConfigurationError as e:
        print "An error occured when trying to read the configuration file 'Configuration.json'."
        print e.message
        sys.exit(3)

    except R2D2_DatabaseError as e:
        print "An error occured when trying to connect to the database."
        print e.message
        sys.exit(4)
