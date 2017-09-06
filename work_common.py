import configparser
import os.path
import time
import re

config_file = os.path.expanduser('~/.work_config')
work_file = os.path.expanduser('~/.work')

# Read the user config
config = configparser.ConfigParser()
config.read(os.path.expanduser("~/.work_config"))

# Helper functions in general
def now():
    return str(int(time.time()))

def parse_work_line(line):
    match = re.search('@(?P<extratime>-?[0-9]+)-(?P<time>[0-9]{10})(?P<name>.+)', line)
    if match:
        return { 'action': '@',
                 'time': int(match.group('time')),
                 'name': match.group('name'),
                 'extratime': int(match.group('extratime')) }
    match = re.search('(?P<action>.)(?P<time>[0-9]{10})(?P<name>.+)', line)
    return { 'action': match.group('action'),
             'time': int(match.group('time')),
             'name': match.group('name')}

# Helper functions for manipulating the work file
def report_start(name):
    with open(work_file, 'a') as f:
        f.write('+{}{}\n'.format(now(), name))
    return 0

def report_stop(name):
    with open(work_file, 'a') as f:
        f.write('-{}{}\n'.format(now(), name))
    return 0

def report_restart(name):
    with open(work_file, 'a') as f:
        f.write('<{}{}\n'.format(now(), name))
    return 0

def report_time(name, extratime):
    with open(work_file, 'a') as f:
        f.write('@{}-{}{}\n'.format(int(extratime), now(), name))
    return 0    

def report_hide(name):
    with open(work_file, 'a') as f:
        f.write('#{}{}\n'.format(now(), name))
    return 0

def get_workday():
    return int(float(config['WORK']['Day']) * 3600)

def get_time(name, total = False):
    worked_seconds = 0
    last_start = 0
    with open(work_file, 'r') as f:
        for line in f:
            work_line = parse_work_line(line)
            if work_line['name'] != name:
                continue
            # Stop Work
            if work_line['action'] == '-' and last_start != 0:
                worked_seconds += work_line['time'] - last_start
                last_start = 0
            # Start Work
            elif work_line['action'] == '+' and last_start == 0:
                last_start = work_line['time']
            # Restart Work (like a stop and start)
            elif work_line['action'] == '<':
                if last_start != 0:
                    worked_seconds += work_line['time'] - last_start
                if total == False:
                    worked_seconds = 0
                last_start = work_line['time']
            # Report extra time
            elif work_line['action'] == '@':
                worked_seconds += work_line['extratime']

    if last_start != 0:
        worked_seconds += int(now()) - last_start
    return worked_seconds

def get_active_work_names():
    work_names = []
    with open(work_file, 'r') as f:
        for line in f:
            work_line = parse_work_line(line)
            if work_line['action'] == '-' and work_line['name'] in work_names:
                work_names.remove(work_line['name'])
            if ((work_line['action'] == '+' or work_line['action'] == '<')
                and work_line['name'] not in work_names):
                work_names.append(work_line['name'])
    return work_names

def get_visible_work_names():
    work_names = []
    with open(work_file, 'r') as f:
        for line in f:
            work_line = parse_work_line(line)
            if work_line['action'] == '#' and work_line['name'] in work_names:
                work_names.remove(work_line['name'])
            if work_line['action'] != '#' and work_line['name'] not in work_names:
                work_names.append(work_line['name'])
    return work_names
    
def get_all_work_names():
    work_names = []
    with open(work_file, 'r') as f:
        for line in f:
            work_line = parse_work_line(line)
            if work_line['name'] not in work_names:
                work_names.append(work_line['name'])
    return work_names
