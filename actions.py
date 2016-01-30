from settings import JOB_MODULE
from task import Task


def upload_job(handler):
    data = handler.get_post_data()
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


def add_task(handler):
    data = handler.get_post_data()
    ret = "ok"
    try:
        handler.server.manager.jobs.put(Task(data))
    except IndexError:
        ret = "bad"
    return {
        "status": ret
    }


def status(handler):
    return {
        "queue_size": handler.server.manager.jobs.qsize(),
        "worker_count": handler.server.manager.worker_count,
        "active_workers": handler.server.manager.active_count.value
    }
