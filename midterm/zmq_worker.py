import zmq
from  multiprocessing import Process
import csv

x_count=0
y_count=0

def voting_station_worker():
    context = zmq.Context()
    receiver = context.socket(zmq.PULL)
    receiver.connect("tcp://127.0.0.1:4000")
    
    result_sender = context.socket(zmq.PUSH)
    result_sender.connect("tcp://127.0.0.1:3000")
    
    msg = receiver.recv_json()
    region = msg['region']
    print(f'region={region} to count votes')
    result = {}
    global x_count
    global y_count
    # scan file and count votes
    if region == 'east':
        # FIXME
        # Count votes from east.cvs
        process_file('east')
        print(f'Counting {region}...')
        # FIXME
        result = {
            'region': region,
            'x': x_count,
            'y': y_count
        }
    else:
        # FIXME
        # Count votes from west.cvs
        process_file('west')
        print(f'Counting {region}...')
        # FIXME
        
        result = {
            'region': region,
            'x': x_count,
            'y': y_count
        }
    
    print(f'result={result}')
    result_sender.send_json(result)
    print('Finished the worker')
    
    
def process_file(region):
    filename='./votes/'+ str(region)+'.csv'
    if region=='east' or region=='west':
        with open(filename, newline='') as csvfile:
            data = csv.reader(csvfile, delimiter=' ')
            for row in data:
                if row[0]=='x':
                    global x_count
                    x_count += 1
                elif row[0]=='y':
                    global y_count
                    y_count += 1

    else:
        print("Error: Invalid region name")

        

if __name__ == "__main__":
    voting_station_worker()