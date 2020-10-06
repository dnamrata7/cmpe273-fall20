# Lab 2

Implement a master-work pattern to calculate the square root of the numbers.

## Components

```

                       PUSH      PULL      PUSH 
|--------------------| ------> | Worker | -------> |-----------|
| Generator (Master) | ------> | Worker | -------> | Dashboard |
|--------------------| ------> | Worker | -------> |-----------|

```

* Generator

The generator component generates a list of numbers from 0 to 10,000 and sends (PUSH) those numbers to Worker.


* Worker

The worker component listens (PULL) the numbers from the generator in a round robin fashion and calculate a square root of the numbers. Finally, sends the result to the dashboard.


* Dashboard

The dashboard component receives the result from the workers and displays the result to the console.

