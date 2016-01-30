from datetime import datetime
import importlib
from settings import JOB_MODULE, EXIT_NAME


class Task(object):

    def __init__(self, data):
        if "name" not in data:
            raise ValueError("Task must have name field in data.")
        self.name = data.get("name")[0]
        self.priority = int(data.get("priority", [0])[0])
        self.status = "queued"
        self.params = {"name": self.name} # TODO figure out how to handle json post requests so that this can be a json.loads
        self.created = str(datetime.now())

    def run(self):
        module = importlib.import_module("{0}.{1}".format(JOB_MODULE, self.name))
        method = getattr(module, "run")
        return method(self.params)

exit_task = Task({"name": EXIT_NAME})


def task_worker(work_queue, active_workers):
    while True:
        task = work_queue.get()
        active_workers.value += 1
        print("Working on: {0} Queue Size: {1}".format(task.name, work_queue.qsize()))
        if task.name == exit_task.name:
            print("Exiting..")
            break
        task.run()
        print("Finished task..")
        active_workers.value -= 1