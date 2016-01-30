from multiprocessing import Process, Value
from task import exit_task, task_worker


class WorkerManager(object):

    def __init__(self, jobs, worker_count, initialize=False, worker=task_worker, exit_signal=exit_task):
        self.jobs = jobs
        self.worker = worker
        self.exit_signal = exit_signal
        self.workers = []
        self.worker_count = worker_count
        self._initialized = False
        self.active_count = Value("i", 0)
        if initialize:
            self.init_workers()

    def init_workers(self):
        print("Initializing {0} workers.".format(self.worker_count))
        self._initialized = True
        for i in range(self.worker_count):
            worker = Process(target=self.worker, args=(self.jobs, self.active_count))
            self.workers.append(worker)
            worker.start()

    def shutdown(self):
        print("Shutting down {0} workers.".format(self.worker_count))
        for worker in self.workers:
            self.jobs.put(self.exit_signal)
            worker.join()
        self._initialized = False

    def are_workers_active(self):
        return self._initialized