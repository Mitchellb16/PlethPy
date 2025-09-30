# -*- coding: utf-8 -*-
"""
Created on Tue Sep 30 18:35:02 2025

@author: mitch
"""

import os

# 1. Get the absolute path of the directory containing this file (app/)
APP_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. Get the project root (the directory above app/)
PROJECT_ROOT = os.path.dirname(APP_DIR)

# 3. Define all other important paths relative to the ones above
RESOURCES_DIR = os.path.join(APP_DIR, 'resources')
# Add other paths here as your project grows, e.g., LOGS_DIR, DATA_DIR, etc.