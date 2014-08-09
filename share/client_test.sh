#!/bin/bash

export HOST="localhost:5000"

function prepare() {
    [ -f jsawk ] || {
        echo "> Preparation"
        echo ">> Downloading jsawk"
        wget https://raw.githubusercontent.com/micha/jsawk/master/jsawk
    }

    [ -f resty] || {
        echo ">> Downloading resty"
        wget http://github.com/micha/resty/raw/master/resty
        chmod 755 jsawk resty
        echo "> End Preparation"
    }

    source ./resty $HOST

}


function open_session() {
    echo "Starting session"
    TOKEN=$(GET "/session" | jsawk 'token')
}


prepare

open_session
