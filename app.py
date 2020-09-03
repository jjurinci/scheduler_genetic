from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from compute_thread import Compute
import json
import uuid

app = Flask(__name__)
cors = CORS(app)

#client = MongoClient("")
#db = client.scheduler

@app.route('/')
def hello():
    return "Hello world!"

@app.route('/solve', methods=['POST'])
def solve():
    data = request.get_data()
    data = json.loads(data.decode('utf-8'))
    
    solver_id = str(uuid.uuid4())
    
    data["data"]["solverId"] = solver_id
    
    thread_a = Compute(data)
    thread_a.start()
    
    response = app.response_class(
        response = json.dumps(data),
        status = 202,
        mimetype = 'application/json'
    )
    return response
    

@app.route('/solver_results/<userid>/<solverid>', methods=["GET"])
def solve_results(userid, solverid):
    results = db.solver_results.find({'$and':[ {'solverId':solverid} ,{'userId': userid} ]})
    results = list(results)
    for r in results: r['_id'] = str(r['_id'])

    status = 200 if results else 404
    response = app.response_class(
        response = json.dumps(results),
        status = status,
        mimetype = 'application/json'
    )

    return response

@app.route('/stop_solver', methods = ["POST"])
def stop_solver():
    data = request.get_data()
    data = json.loads(data.decode('utf-8'))["data"]

    x = db.solver_stop.insert_one(data)
    data_response = str(x.inserted_id) if x else ""
    status = 200 if x else 400

    response = app.response_class(
        response = json.dumps(data_response),
        status = status,
        mimetype = 'application/json'
    )
    return response

@app.route('/solver_timetables/<userid>/<solverid>', methods=["GET"])
def solver_timetables(userid, solverid):
    result = db.solver_timetables.find_one({'$and':[ {'solverId':solverid} ,{'userId': userid} ]})
    if result: result['_id'] = str(result['_id'])

    status = 200 if result else 404
    response = app.response_class(
        response = json.dumps(result),
        status = status,
        mimetype = 'application/json'
    )
    clear_solver(userid, solverid)
    return response   

def clear_solver(userId, solverId):
    db.solver_results.delete_many({'$and': [{'solverId':solverId}, {'userId':userId}]})
    db.solver_stop.delete_many({'$and': [{'solverId':solverId}, {'userId':userId}]})


@app.route('/clear_solver_results', methods=["GET"])
def clear():
    db.solver_results.delete_many({})
    db.solver_stop.delete_many({})
    db.solver_timetables.delete_many({})
    response = app.response_class(
        response = [],
        status = 200,
        mimetype = 'application/json'
    )
    return response

if __name__ == '__main__':
    app.run()
