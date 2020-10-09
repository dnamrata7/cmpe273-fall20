import yaml
import sys
import schedule
import time
from datetime import datetime
import urllib3

days = ['sunday','monday','tuesday','wednesday','thursday','friday','saturday','sunday']
http = urllib3.PoolManager()
data={}

# Parse the yaml file 
def parse_file(fileName):
    with open(fileName, 'r') as stream:
        try:
            global data
            data = yaml.safe_load(stream)
            run_scheduler(data)
        except yaml.YAMLError as exc:
            print(exc)

# To schedule the job according to given cron job format 
def run_scheduler(data):
    when = data['Scheduler']['when'].split()
    min=when[0]
    hr=when[1]
    day=when[2]
    time_unit=''

    if hr=='*':
        time_unit='00:'
    else:
        if int(hr)<10:
            hr = '0'+hr
        time_unit=hr+":"
    
    if min=='*':
        time_unit +='00'
    else:
        if int(min)<10:
            min = '0'+min
        time_unit += min
    
    if day=='*':
        if hr=='*' and min=='*':
            print("Error: Invalid format")
        elif hr=='*' and min != '*':
            schedule.every(int(min)).minutes.do(job)
        elif int(hr)<= 23 and int(hr)>=0:
            schedule.every().day.at(time_unit).do(job)
    elif int(day)<=7 and int(day)>=0:
        if hr=='*' and min != '*':
            # 2 * 1
            cmd= "schedule.every()." + days[int(day)] + ".do(day_minutely_job, min)"
        else:
            # 2 1 1       * 1 2
            cmd= "schedule.every()." +days[int(day)] + ".at(\"" + time_unit + "\").do(job)"
        exec(cmd)
    else:
         print("Error: Invalid chron format")
        
    while True:
        schedule.run_pending()
        time.sleep(1)    


def day_minutely_job(min):
    schedule.every(int(min)).minutes.do(job)


def job():
    for i in data['Scheduler']['step_id_to_execute']:
        execute_step(i,None)
   
        
#Execute the step with given id
def execute_step(step_id_to_execute,input_data):
    step_data = data['Steps'][int(step_id_to_execute)-1][step_id_to_execute]
    if step_data['type']== 'HTTP_CLIENT':
        if(input_data is None):
            outbound_url=step_data['outbound_url']
        else:
            outbound_url = input_data
        response = http.request(step_data['method'],outbound_url)
        if(response.status==200):
            action = step_data['condition']['then']['action'].split(':')
            action_data= step_data['condition']['then']['data']
            if(action[-1]=='print'):
                print(response.headers[action_data.split('.')[-1]])
            elif(action[-3]=='invoke' and action[-2]=='step'):
                execute_step(int(action[-1]),action_data)

        else:
            print("Error")
    

if __name__=="__main__":
    try:
        fileName=sys.argv[1]
        parse_file(fileName)
        pass
    except Exception as e:
        print("You must provide a valid filename as parameter")
        raise