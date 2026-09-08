#!/usr/bin/env python
"""
local-vision-agent skill adapter for Hermes CLI.
"""

import subprocess
import sys
import os

def run(args):
    """Run the vision agent script with given args."""
    # Get the directory of this skill.py
    skill_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(skill_dir, 'scripts', 'vision_agent.py')
    
    # Build command: python script_path args
    cmd = [sys.executable, script_path] + args
    
    # Run the command and return the result
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Print stdout and stderr as appropriate
    if result.stdout:
        sys.stdout.write(result.stdout)
    if result.stderr:
        sys.stderr.write(result.stderr)
    
    return result.returncode

def hello():
    """Return a greeting message."""
    return "local-vision-agent skill ready"

if __name__ == '__main__':
    # If run directly, forward arguments to run function
    sys.exit(run(sys.argv[1:]))