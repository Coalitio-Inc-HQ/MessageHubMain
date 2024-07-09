#!/bin/bash
ls
alembic upgrade head 
python run_server.py