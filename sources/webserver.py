from flask import Flask, request, Response, json
import pymongo

from db_api_wrapper import DBWrapper
import configuration

app = Flask(__name__)


@app.route('/items', methods = ['GET'])
def variables():
    subreddit = request.args.get("subreddit")
    t1 = request.args.get("t1")
    t2 = request.args.get("t2")
    kw = request.args.get("keyword")

    try:
        config = configuration.getConfiguration()
        db = DBWrapper(config["database"])

        query = getQuery(subreddit, t1, t2, kw)

        cursor = db.items.find(filter=query,
                               projection={"_id": 0},
                               sort=[("timestamp", pymongo.DESCENDING)])

        print cursor.explain()

        data = list(cursor)
        response = Response(response=json.dumps(data),
                            status=200,
                            mimetype='application/json')
    except Exception as e:
        msg = "An error occured: " + e.message + "<br/>"
        msg += "Query string should be similar to : /items?subreddit=&ltsubreddit&gt&from=&ltt1&gt&to=&ltt2&gt&keyword=&ltkw&gt <br/>"
        msg += "where keyword is optional and the other parameters are mandatory"

        response = Response(response=msg,
                           status=404)

    return response


def getQuery(subreddit, t1, t2, keyword):
    query = {"subreddit": {"$eq": subreddit},
             "timestamp": {"$gte": float(t1), "$lt": float(t2)}}

    if keyword:
        query["$text"] = { "$search": keyword }

    return query


@app.route('/all')
def listAll():
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
    config = configuration.getConfiguration()

    app.run(
        host=config["webserver"]["host"],
        port=int(config["webserver"]["port"]))