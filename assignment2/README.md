# Assignment 2

## Dependency

- [Requests](https://requests.readthedocs.io/en/master/)
- [Schedule](https://github.com/dbader/schedule)

## Requirements

You will be building low-code/no-code HTTP client application that supports these features:

* Outbound HTTP GET calls
* Handle logic based on the response as INPUT.
* Trigger OUTPUT event based on the logic.
* Scheduler to execute the steps.


### Scheduler 'when' Format

```
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23) 
│ │ ┌───────────── day of week (0 - 6) (Sunday to Saturday; 
| | |                                      7 is also Sunday some systems)
│ │ │
│ │ │ 
│ │ │ 
│ │ │ 
│ │ │
* * * 
```

_Example_

```
5 * * 
# Executes at every 5 minutes

* 2 * 
# Executes at every day at 02:00

* * 1 
# Executes at every Monday at 00:00

5 1 * 
# Executes at 1:05

10 23 * 
# Executes at 23:10

10 23 1 
# Executes at 23:10 on every Monday
```

_Flow Syntax_

```yaml
Steps:
 - 1:
    type: HTTP_CLIENT
    method: GET
    outbound_url: http://requestbin.com/
    condition:
      if: 
        equal:
          left: http.response.code
          right: 200
      then:
        action: ::print
        data: http.response.body
      else:
        action: ::print
        data: "Error"
    
Scheduler:
  when: "5 * *"
  step_id_to_execute: [ 1 ]
```

Save the flow in _input.yaml_

## How to execute Flow Http Client

```
python3 httpflow.py input.yaml
```

### Expected Output

Print the output in every five minutes.

```
Response body

OR

Error
```

## Keywords


* ::invoke:step:{id}

> Invoke a step by id.

* ::print and _data_

> Print the _data_ to a console.
  
