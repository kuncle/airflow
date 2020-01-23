#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
"""Celery command"""
import os
import signal
import sys
from multiprocessing import Process
from typing import Optional

import daemon
import psutil
from celery.bin import worker as worker_bin
from daemon.pidfile import TimeoutPIDLockFile
from lockfile.pidlockfile import read_pid_from_pidfile, remove_existing_pidfile

from airflow import settings
from airflow.configuration import conf
from airflow.executors.celery_executor import app as celery_app
from airflow.utils import cli as cli_utils
from airflow.utils.cli import setup_locations, setup_logging, sigint_handler
from airflow.utils.serve_logs import serve_logs

WORKER_PROCESS_NAME = "worker"


@cli_utils.action_logging
def flower(args):
    """Starts Flower, Celery monitoring tool"""
    broker = conf.get('celery', 'BROKER_URL')
    address = '--address={}'.format(args.hostname)
    port = '--port={}'.format(args.port)
    api = ''  # pylint: disable=redefined-outer-name
    if args.broker_api:
        api = '--broker_api=' + args.broker_api

    url_prefix = ''
    if args.url_prefix:
        url_prefix = '--url-prefix=' + args.url_prefix

    basic_auth = ''
    if args.basic_auth:
        basic_auth = '--basic_auth=' + args.basic_auth

    flower_conf = ''
    if args.flower_conf:
        flower_conf = '--conf=' + args.flower_conf

    if args.daemon:
        pid, stdout, stderr, _ = setup_locations("flower", args.pid, args.stdout, args.stderr, args.log_file)
        stdout = open(stdout, 'w+')
        stderr = open(stderr, 'w+')

        ctx = daemon.DaemonContext(
            pidfile=TimeoutPIDLockFile(pid, -1),
            stdout=stdout,
            stderr=stderr,
        )

        with ctx:
            os.execvp("flower", ['flower', '-b',
                                 broker, address, port, api, flower_conf, url_prefix, basic_auth])

        stdout.close()
        stderr.close()
    else:
        signal.signal(signal.SIGINT, sigint_handler)
        signal.signal(signal.SIGTERM, sigint_handler)

        os.execvp("flower", ['flower', '-b',
                             broker, address, port, api, flower_conf, url_prefix, basic_auth])


def _serve_logs(skip_serve_logs: bool = False) -> Optional[Process]:
    """Starts serve_logs sub-process"""
    if skip_serve_logs is False:
        sub_proc = Process(target=serve_logs)
        sub_proc.start()
        return sub_proc
    return None


@cli_utils.action_logging
def worker(args):
    """Starts Airflow Celery worker"""
    if not settings.validate_session():
        print("Worker exiting... database connection precheck failed! ")
        sys.exit(1)

    autoscale = args.autoscale
    skip_serve_logs = args.skip_serve_logs

    if autoscale is None and conf.has_option("celery", "worker_autoscale"):
        autoscale = conf.get("celery", "worker_autoscale")

    # Setup locations
    pid_file_path, stdout, stderr, log_file = setup_locations(
        process=WORKER_PROCESS_NAME,
        pid=args.pid,
        stdout=args.stdout,
        stderr=args.stderr,
        log=args.log_file,
    )

    # Setup Celery worker
    worker_instance = worker_bin.worker(app=celery_app)
    options = {
        'optimization': 'fair',
        'O': 'fair',
        'queues': args.queues,
        'concurrency': args.concurrency,
        'autoscale': autoscale,
        'hostname': args.celery_hostname,
        'loglevel': conf.get('logging', 'LOGGING_LEVEL'),
        'pidfile': pid_file_path,
    }

    if conf.has_option("celery", "pool"):
        options["pool"] = conf.get("celery", "pool")

    if args.daemon:
        # Run Celery worker as daemon
        handle = setup_logging(log_file)
        stdout = open(stdout, 'w+')
        stderr = open(stderr, 'w+')

        ctx = daemon.DaemonContext(
            files_preserve=[handle],
            stdout=stdout,
            stderr=stderr,
        )
        with ctx:
            sub_proc = _serve_logs(skip_serve_logs)
            worker_instance.run(**options)

        stdout.close()
        stderr.close()
    else:
        # Run Celery worker in the same process
        sub_proc = _serve_logs(skip_serve_logs)
        worker_instance.run(**options)

    if sub_proc:
        sub_proc.terminate()


@cli_utils.action_logging
def stop_worker(args):  # pylint: disable=unused-argument
    """Sends SIGTERM to Celery worker"""
    # Read PID from file
    pid_file_path, _, _, _ = setup_locations(process=WORKER_PROCESS_NAME)
    pid = read_pid_from_pidfile(pid_file_path)

    # Send SIGTERM
    if pid:
        worker_process = psutil.Process(pid)
        worker_process.terminate()

    # Remove pid file
    remove_existing_pidfile(pid_file_path)
