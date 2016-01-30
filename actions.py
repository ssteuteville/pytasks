from settings import JOB_MODULE
from task import Task


def upload_job(path, data):
    status = "ok"
    try:
        name = data["name"][0]
        path = "{0}/{1}.py".format(JOB_MODULE, name)
        script = data["script"][0]
        with open(path, "wb") as f:
            f.write(bytes(script, "UTF-8"))
    except Exception:
        status = "bad"
    return {
        "status": status
    }


def add_task(manager):
    def _action(path, data):
        ret = "ok"
        try:
            manager.jobs.put(Task(data))
        except IndexError:
            ret = "bad"
        return {
            "status": ret
        }
    return _action


def status(manager):
    def _action(path):
        return {
            "queue_size": manager.jobs.qsize(),
            "worker_count": manager.worker_count,
            "active_workers": manager.active_count.value
        }
    return _action
