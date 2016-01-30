from manager import WorkerManager
from multiprocessing import Queue
from settings import WORKER_COUNT, PORT
from server import WorkerServer

job_queue = Queue()
manager = WorkerManager(jobs=job_queue, worker_count=WORKER_COUNT)


if __name__== "__main__":
    server = WorkerServer(('', PORT), manager)
    try:
        print('Started httpserver on port ', PORT)
        server.start()
    except KeyboardInterrupt:
        print('^C received, shutting down the web server')
        server.teardown()