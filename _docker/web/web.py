from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from sqlalchemy import create_engine
# from json import dumps

db_name = "/Users/james/Dropbox/Work/CodeForSanJose/JailStats/dev/jailstats.db"
e = create_engine("sqlite:///{}".format(db_name))

app = Flask(__name__)
api = Api(app)

class MonthlyAPI(Resource):
    def get(self):
        conn = e.connect()
        parser = reqparse.RequestParser()
        parser.add_argument('year', type=int, required=True, help='The year must be specified.')
        parser.add_argument('month', type=int, required=True, help='The month must be specifed.')
        args = parser.parse_args()

        query = conn.execute("select * from daily where Year={} and Month={}".format(args['year'], args['month']))
        result = [dict(zip(tuple(query.keys()), i)) for i in query.cursor]
        return result

api.add_resource(MonthlyAPI, '/api/daily')

if __name__ == '__main__':
    app.run()