#!/usr/pkg/bin/python3.9

#
# Time-stamp: <2022/03/06 15:28:48 (CST) daisuke>
#

#
# radio program recording script for NHK on-demand
#
#    version 1.0: 05/Mar/2022
#

#
# usage:
#
#  downloading files for the program "adventure"
#    % radio_rec_nhk_ondemand.py adventure
#
#  downloading files for the program "genichiro" and "matsuodo"
#    % radio_rec_nhk_ondemand.py genichiro matsuodo
#

# importing argparse module
import argparse

# importing datetime module
import datetime

# importing time module
import time

# importing os module
import os

# importing sys module
import sys

# importing pathlib module
import pathlib

# importing ssl module
import ssl

# importing urllib module
import urllib.request

# importing json module
import json

# importing re module
import re

# importing subprocess module
import subprocess

# importing shutil module
import shutil

# importing random module
import random

# setting for SSL
ssl._create_default_https_context = ssl._create_unverified_context

#
# important paramters
#

# NHK JSON file
url_json_nhk = 'https://www.nhk.or.jp/radioondemand/json/index_v3/index.json'

# radio programs
dic_programs = {
    'adventure':          '0164',
    'amami':              '7226',
    'audiodrama':         '0055',
    'culture_archive':    '1890',
    'culture_art':        '1928',
    'culture_chinese':    '1930',
    'culture_history':    '1927',
    'culture_literature': '1929',
    'culture_science':    '3065',
    'earthradio':         '0184',
    'edoradio':           '7263',
    'genichiro':          '6324',
    'hoshizora':          '3489',
    'jikutabi':           '3393',
    'kotenkyoshitsu':     '6311',
    'mainichi10minyose':  '7241',
    'matsuodo':           '0715',
    'meisakuza':          '0930',
    'nemurenai':          '2401',
    'newsdeeigojutsu':    '4812',
    'nhkjournal':         '0045',
    'nihongojiten':       '0972',
    'okinawanecchuclub':  '0575',
    'shinyabin':          '0324',
    'theatre':            '0058',
    'umicafe':            '6988',
    'weekendsunshine':    '0029',
    'yamacafe':           '4750',
    'yamazakimariradio':  '7239',
    'yamyamplaylist':     '7210',
    }

# date/time
datetime_now = datetime.datetime.now ()
YYYY         = datetime_now.year
MM           = datetime_now.month
DD           = datetime_now.day
hh           = datetime_now.hour
mm           = datetime_now.minute
ss           = datetime_now.second
datetime_str = "%04d%02d%02d_%02d%02d%02d" % (YYYY, MM, DD, hh, mm, ss)
date_str     = "%04d%02d%02d" % (YYYY, MM, DD)

# environmental variables
dir_home = os.environ['HOME']

# process ID
pid = os.getpid ()

# default parameters
choices_programs = dic_programs.keys ()
default_programs = 'adventure'
help_programs    = "program names (default: %s)" % default_programs

default_useragent = \
    'Mozilla/5.0 (X11; NetBSD amd64; rv:96.0) Gecko/20100101 Firefox/96.0'
help_useragent    = "user agent for HTTP retrieval (default: %s)" \
    % default_useragent

default_dir_radio = "%s/audio/radio" % dir_home
help_dir_radio    = "directory to store recorded file (default: %s)" \
    % default_dir_radio

default_dir_tmp = "/tmp/radio_%s_%s" % (datetime_str, pid)
help_dir_tmp    = "directory to store temporary file (default: %s)" \
    % default_dir_tmp

default_ffmpeg = '/usr/pkg/bin/ffmpeg4'
help_ffmpeg    = "location of ffmpeg command (default: %s)" % default_ffmpeg

default_sleep  = 60
help_sleep     = "max sleep time between file retrieval (default: %d sec)" \
    % default_sleep

default_verbose = 0
help_verbose    = "verbosity level (default: %d)" % default_verbose

# construction of parser object
desc = 'NHK on-demand radio program recording script'
parser = argparse.ArgumentParser (description=desc)

# adding arguments
parser.add_argument ('programs', nargs='+', choices=choices_programs, \
                     help=help_programs)
parser.add_argument ('-r', '--radio-dir', default=default_dir_radio, \
                     help=help_dir_radio)
parser.add_argument ('-t', '--temporary-dir', default=default_dir_tmp, \
                     help=help_dir_tmp)
parser.add_argument ('-u', '--user-agent', default=default_useragent, \
                     help=help_useragent)
parser.add_argument ('-f', '--ffmpeg', default=default_ffmpeg, \
                     help=help_ffmpeg)
parser.add_argument ('-s', '--sleep', default=default_sleep, \
                     help=help_sleep)
parser.add_argument ('-v', '--verbose', action='count', \
                     default=default_verbose, help=help_verbose)

# command-line argument analysis
args = parser.parse_args ()

# parameters
list_programs  = args.programs
dir_radio      = args.radio_dir
dir_tmp        = args.temporary_dir
user_agent     = args.user_agent
command_ffmpeg = args.ffmpeg
max_sleep_time = args.sleep
verbosity      = args.verbose

# files
file_json_nhk = "%s/index.json" % dir_tmp

# existence check of commands
list_commands = [command_ffmpeg]
for command in list_commands:
    # making a pathlib object
    path_command = pathlib.Path (command)
    # if command does not exist, then stop the script
    if not (path_command.exists ()):
        # printing message
        print ("The command \"%s\" does not exist!" % command)
        print ("Install the command \"%s\" and then run the command again." \
               % command)
        # exit
        sys.exit ()

# existence check of directories
list_dir = [dir_radio, dir_tmp]
for directory in list_dir:
    # making pathlib object
    path_dir = pathlib.Path (directory)
    # if directory does not exist
    if not (path_dir.exists ()):
        # printing message
        if (verbosity):
            print ("# making directory \"%s\"..." % directory)
        # making directory
        path_dir.mkdir (parents=True, exist_ok=True)
        # printing message
        if (verbosity):
            print ("# finished making directory \"%s\"!" % directory)

# retrieval of JSON file from NHK website
req_nhk = urllib.request.Request (url=url_json_nhk)
req_nhk.add_header ('User-Agent', user_agent)
with urllib.request.urlopen (req_nhk) as www:
    data_json_nhk = www.read ()

# decoding JSON file content
text_json_nhk = data_json_nhk.decode ('utf8')

# writing JSON file into file
with open (file_json_nhk, 'w') as fh:
    fh.write (text_json_nhk)

# decoding JSON data
dic_nhk = json.loads (text_json_nhk)

#
# finding detailed information about target programs
#

# initialisation of a dictionary
dic_detailed_json = {}
# checking information of each program in JSON file
for i in range (len (dic_nhk['data_list'])):
    # matching with each target program
    for program in list_programs:
        # acquiring program ID
        program_id = dic_programs[program]
        # if program ID matches, add information to dictionary
        if (dic_nhk['data_list'][i]['site_id'] == program_id):
            dic_detailed_json[program] = dic_nhk['data_list'][i]['detail_json']

#
# processing for each program
#
for program in dic_detailed_json:
    if (verbosity):
        print ("# processing program \"%s\"..." % program)
    # retrieving JSON file for detailed information about program
    url_json_program = dic_detailed_json[program]
    req_program = urllib.request.Request (url=url_json_program)
    req_program.add_header ('User-Agent', user_agent)
    with urllib.request.urlopen (req_program) as www:
        data_json_program = www.read ()
    text_json_program = data_json_program.decode ('utf8')

    # writing JSON file into a file
    file_json_program = "%s/%s.json" % (dir_tmp, program)
    with open (file_json_program, 'w') as fh:
        fh.write (text_json_program)

    # decoding JSON data
    dic_detail = json.loads (text_json_program)

    # processing for each audio stream
    for j in range (len (dic_detail['main']['detail_list'])):
        # URL of m3u8
        url_m3u8 = \
            dic_detail['main']['detail_list'][j]['file_list'][0]['file_name']

        # information of date/time of start of program
        aa_vinfo4 = \
            dic_detail['main']['detail_list'][j]['file_list'][0]['aa_vinfo4']

        # pattern matching of date/time of start of program
        pattern_date = re.compile ('(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})\+09:00_')
        match_date = re.search (pattern_date, aa_vinfo4)
        if (match_date):
            start_YYYY = int (match_date.group (1))
            start_MM   = int (match_date.group (2))
            start_DD   = int (match_date.group (3))
            start_hh   = int (match_date.group (4))
            start_mm   = int (match_date.group (5))
            start_ss   = int (match_date.group (6))
        else:
            if (verbosity):
                print ("pattern matching failed!")
            continue

        # file names
        file_aac_tmp = "%s/%s_%04d%02d%02d_%02d%02d.aac" \
            % (dir_tmp, program, start_YYYY, start_MM, start_DD, \
               start_hh, start_mm)
        file_aac     = "%s/%s_%04d%02d%02d_%02d%02d.aac" \
            % (dir_radio, program, start_YYYY, start_MM, start_DD, \
               start_hh, start_mm)

        if (verbosity):
            print ("#    fetching file \"%s\"..." % file_aac_tmp)

        # sleeping for a short time
        sleep_time = random.randint (5, max_sleep_time)
        time.sleep (sleep_time)
            
        # command for fetching audio stream using ffmpeg command
        command_fetch = "%s -n -i '%s' -vn -acodec aac %s" \
            % (command_ffmpeg, url_m3u8, file_aac_tmp)
        if (verbosity):
            print ("#    %s" % command_fetch)
        subprocess.run (command_fetch, shell=True)
        
        # existence check of fetched audio file
        path_aac_tmp = pathlib.Path (file_aac_tmp)
        if not (path_aac_tmp.exists ()):
            # printing message
            print ("The file \"%s\" does not exist!" % file_aac_tmp)
            print ("Something is wrong with retrieval of data.")
            print ("Exiting...")
            # exit
            sys.exit ()

        # file size of file_aac_tmp
        filesize_aac_tmp = path_aac_tmp.stat ().st_size

        # file size of file_aac
        path_aac = pathlib.Path (file_aac)
        if (path_aac.exists ()):
            filesize_aac = path_aac.stat ().st_size
        else:
            filesize_aac = 0

        # printing file sizes
        if (verbosity):
            print ("#    file sizes")
            print ("#      %s: %d byte" % (file_aac_tmp, filesize_aac_tmp) )
            print ("#      %s: %d byte" % (file_aac, filesize_aac) )
    
        # copying AAC file
        if ( (path_aac.exists ()) and (filesize_aac >= filesize_aac_tmp) ):
            # if file exists and larger than new file, then not copying file
            if (verbosity):
                print ("#    file \"%s\" is not copied to %s" \
                       % (file_aac_tmp, dir_radio) )
        else:
            if (verbosity):
                print ("#    copy: %s ==> %s" % (file_aac_tmp, file_aac) )
            # copying file
            shutil.copy2 (file_aac_tmp, file_aac)
            if (verbosity):
                print ("#    file copy finished")
