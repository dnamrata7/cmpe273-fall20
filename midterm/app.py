import zmq_master
import time
from flask import Flask


app = Flask(__name__)
app.config["DEBUG"] = True

@app.route('/')
def root():
    return 'Election 2020'

@app.route('/result')
def calculate_result(): 
    zmq_master.send_to_voting_workers()
    time.sleep(5)
    result = zmq_master.receive_result()
    return {
        'x_votes': result['x_votes'],
        'y_votes': result['y_votes'] 
    }
    
app.run()