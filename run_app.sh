#!/bin/bash

# hypercorn --workers 8 app:app

hypercorn --bind 0.0.0.0:8000 app:app
