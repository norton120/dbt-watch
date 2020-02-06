#!/usr/local/bin/python3
from flask import jsonify
import subprocess
import click
import os
from flask import Flask, render_template
from time import sleep
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import logging

is_running_tests=False
status='watching'
result='no result'

logger=logging.getLogger()
logger.setLevel(logging.INFO)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

def dbt_run_from_cli(file_event):
    global is_running_tests,status,response
    if not is_running_tests:
        is_running_tests=True
        try:
            if file_event.src_path.endswith('.sql'):
                dbt_model=os.path.basename(file_event.src_path)[:-4]
                response=subprocess.run(['echo',dbt_model])
                status=response.returncode
                result=response.stdout
        except:
            pass
        finally:
            is_running_tests=False
    
@click.group()
def cli():
    pass

@cli.command()
@click.argument('path', default=os.getcwd(), type=click.Path(exists=True))
def watch(path: click.Path) -> None:
    """watches the provided directory (defaults to current directory."""
    logger.critical(f'watching directory {os.path.abspath(path)}...')
    file_events_handler=PatternMatchingEventHandler(patterns="*.sql",
                                ignore_directories=True,
                                case_sensitive=True)



    file_events_handler.on_modified=dbt_run_from_cli
    file_events_handler.on_created=dbt_run_from_cli

    file_observer=Observer()
    file_observer.schedule(file_events_handler,
             path,
             recursive=True)
    file_observer.start()
    app.run(host='0.0.0.0', port=8100,debug=True)
    file_observer.stop()
    file_observer.join()
    logger.critical('stopped flask and watchdog')

@app.route('/')
def serve_index():
    return render_template('status_page.html')

@app.route('/status')
def respond_with_status():
    global result, status
    return jsonify(result=result,status=status)

    

if __name__ == "__main__":
    watch()
