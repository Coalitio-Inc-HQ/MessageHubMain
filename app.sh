#!/bin/bash
sleep 10 && alembic upgrade head && python run_server.py  