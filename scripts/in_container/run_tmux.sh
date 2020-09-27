#!/usr/bin/env bash
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
if [[ ${START_AIRFLOW:="false"} == "true" ]]; then

    ln -s "${IN_CONTAINER_DIR}/stop_tmux_airflow.sh" stop_airflow.sh

    export AIRFLOW__CORE__LOAD_DEFAULT_CONNECTIONS=${LOAD_DEFAULT_CONNECTIONS}
    export AIRFLOW__CORE__LOAD_EXAMPLES=${LOAD_EXAMPLES}

    #this is because I run docker in WSL - Hi Bill!
    export TMUX_TMPDIR=~/.tmux/tmp
    mkdir -p ~/.tmux/tmp
    chmod 777 -R ~/.tmux/tmp

    # Set Session Name
    export TMUX_SESSION="Airflow"

    # Start New Session with our name
    tmux new-session -d -s "${TMUX_SESSION}"

    # Name first Pane and start bash
    tmux rename-window -t 0 'Main'
    tmux send-keys -t 'Main' 'bash' C-m 'clear' C-m

    tmux split-window -v
    tmux select-pane -t 1
    tmux send-keys 'airflow scheduler' C-m

    tmux split-window -h
    tmux select-pane -t 2
    tmux send-keys 'airflow webserver' C-m

    # Attach Session, on the Main window
    tmux select-pane -t 0
    tmux send-keys "./scripts/in_container/run_tmux_welcome.sh" C-m

    tmux attach-session -t "${TMUX_SESSION}":0
fi
