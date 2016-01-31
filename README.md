# pytasks
Task Queuing Application

This project aims to be a light weight http server that can schedule and run tasks. The project should remain pure python and never rely on 3rd party libraries. The current implementation uses a multiprocessing queue with NUM_WORKERS amount of child processes always alive and waiting for something to be ready in the queue. When the worker is able to get something from the queue it will import the correct module from JOB_MODULE and run the run(data) method from that module.

## Job: 
Currently any python script that, implements: 
    
    def run(data):
and can run in the same environment as the server is a valid job.

## Task:
Tasks are how jobs that need to run are represented in the work queue. Currently tasks are named after the file that was uploaded.

## Usage:
Starting the server:

    python runner.py

Uploading a job:
    
    multipart/form-data with params: script = file, name = filename w/o extension
    localhost:8000/upload-job
  
Adding a task:
    
    application/x-www-form-urlencoded with param: name
    localhost:8000/add-task
  
Checking queue status:
    
    GET localhost:8000/status
