# importing Flask and other modules
import os
from multiprocessing import Process
from subprocess import Popen, PIPE

from flask import Flask, request, render_template, Response, redirect, flash
# we import waitress here.
from waitress import serve

_main_html: str = "main.html"
_SUBPROCESS: {str: Popen} = {}
_server: Process

# Flask constructor
app = Flask(__name__, static_folder="static/", template_folder="templates/")
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


# which URL is associated function
@app.route('/', methods=["POST", "GET"])
def main():
    return redirect("/run_task", code=307)


@app.route('/run_task', methods=["POST", "GET"])
def run_rask():
    if request.method == "GET":
        return render_template(_main_html)

    task = request.form.get("task")
    task_type = request.form.get("task_type")

    return redirect(f"/run_task/task={task}&task_type={task_type}", code=307)


@app.route('/run_task/task=<task>&task_type=<task_type>', methods=["POST", "GET"])
def run_task_by_id(task: str, task_type: str):
    global _SUBPROCESS

    l_task = task.split(",")

    l_group_id = l_task[0]
    l_task_id = l_task[1]

    _SUBPROCESS.setdefault(task)

    if _SUBPROCESS[task] is None:
        os.environ["PYTHONUNBUFFERED"] = "1"

        _SUBPROCESS[task] = Popen(['spark-submit', 'pyspark_task.py',
                                   "-g", l_group_id,
                                   "-t", l_task_id,
                                   "-tt", task_type],
                                  cwd=os.environ.get("SPARK_APPS"),
                                  stdout=PIPE,
                                  stderr=PIPE, )

    return render_template(_main_html,
                           task=task,
                           task_type=task_type)


def flask_logger(task):
    """creates logging information"""

    if task not in _SUBPROCESS.keys():
        yield f"Task {task} execution has not been started"
    else:
        l_subprocess = _SUBPROCESS[task]

        for l_output in [l_subprocess.stdout, l_subprocess.stderr]:

            l_line = l_output.readline()

            while l_line:

                if l_line:
                    yield l_line.rstrip() + "\n".encode()

                l_line = l_output.readline()

            l_output.close()

        l_subprocess.wait()

        del _SUBPROCESS[task]


@app.route("/log_stream/<task>", methods=["GET"])
def log_stream(task):
    """returns logging information"""
    return Response(flask_logger(task), mimetype="text/plain", content_type="text/event-stream")


def create_app():
    serve(app, host='0.0.0.0', port=5000)


if __name__ == '__main__':
    create_app()
    # app.run(host='0.0.0.0', port=5000, debug=True)