#!/usr/bin/python

"""
What this script does:
  1) reads from 1 or more files
  2) sorts all lines in the file
  3) removes duplicates (if any)
  4) saves the sorted lines to a new file

How to:
  1) Ensure you have Python 2.7 installed and a working virtual environment
  2) Run the script: python sorter.py, arguments can be passed, see below
      python sorter.py small_example
  3) A new file named sorted.dat with the concatentated results will be in the directory
"""

import heapq  # for merging files
import math  # calculating logarithms
import os  # for file-system purposes
import platform  # for identifying operating system
import re
import sys  # for command-line arguments
import tempfile  # for creating temporary directory
import time  # for calculating running time
import unicodedata  # stripping non-printing characters
from glob import glob  # for grabbing files from directory via wildcards

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Let's define some variables
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
strip_whitespace = True # remove whitespace characters of each line

outfile = 'sorted.dat'  # file to save to (changable via -o switch)

remove_duplicates = True

# size to split the output file into (output files will not exceed this number of bytes)
split_size   = 1024 * 1024 * 1024 * 1 # 1GB

# size to split input files into (use a smaller number for less RAM usage)
chunk_size   = 1024 * 1024 * 75       # 75MB

# number of duplicated words removed
words_removed_duplicates  = 0

rjust = 28 # column length for file names. used for right-justification
njust = 13 # column length for word totals.

delete_input = False # delete the input file(s) after data is parsed.

# temporary directory
temp_dir = tempfile.mkdtemp(prefix='sort')
if not temp_dir.endswith(os.sep): temp_dir += os.sep

# frequency variables
freq_flag       = False  # sort list by how frequently the lines appeared (most frequent first)
freq_show_count = False  # display the number of times a word appeared
freq_min        = 0      # minimum times a word must appear to be counted as 'frequent'

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Extract data from the input files
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# first part of the sorting process
# input: list of files, output: single file containing all data
def split(files):
  global split_size, remove_duplicates
  
  split_file = 0  # current chunk filename we are creating
  bytes_cur  = 0  # current amount of bytes in this chunk (not to exceed chunk_size)
  lst        = [] # contains lines of current chunk
  
  words_total, words_kept, files_loaded= 0, 0, 0 # counters
  
  still_sorted = True
  for file in files: # iterate over every file in input
    
    if not os.path.exists(file):
      print '\n file not found: "' + file + '"',
      sys.stdout.flush()
      continue

    elif not os.path.isfile(file):
      print '\n skipping directory: "' + file + '"',
      sys.stdout.flush()
      continue
    
    print ''
    files_loaded += 1
    
    words_in_file, words_created = 0, 0
    file_cur, file_len = 0, os.path.getsize(file) # current/total bytes in this file
    
    last = ''
    
    i = open(file, 'rb')
    line = i.readline()
    while line:
      if strip_whitespace:  # check for white-space stripping
       line = line.strip()
      elif line.endswith('\n') != -1:
       line = line.replace('\n', '')
      
      save = True  # flag, tells us if line should be saved
      
      if save: # if we are still supposed to save it, do it
        bytes_cur += len(line) + 1
        lst.append(line)
        words_kept += 1
        
        if still_sorted and cmp(last, line) > 0:
          still_sorted = False
      
      # check if we have exceeded the chunk size while iterating over this file
      if bytes_cur >= chunk_size: 
        print '\r loading%s, words: %s *sorting*' % (filename(file).rjust(rjust), format(words_in_file + words_created, ',d').rjust(njust)),
        sys.stdout.flush()
        
        if not still_sorted: # the list is not already sorted
          lst.sort()         # sort the chunk
        still_sorted = True
        
        print '\r loading%s, words: %s *chunking*' % (filename(file).rjust(rjust), format(words_in_file + words_created, ',d').rjust(njust)),
        sys.stdout.flush()
        
        o = open(temp_dir + str(split_file), 'wb') 
        for item in lst: # save the chunk
          o.write(item + '\n')
        o.close()
        
        del lst[:]
        
        split_file += 1  # increment the current chunk file
        bytes_cur = 0
        
        print '\r loading%s, words: %s           ' % (filename(file).rjust(rjust), format(words_in_file + words_created, ',d').rjust(njust)),
        sys.stdout.flush()
        
      last = line
      line = i.readline()
    
    i.close()
    print '\r loaded %s, words: %s           ' % (filename(file).rjust(rjust), format(words_in_file + words_created, ',d').rjust(njust)),
    sys.stdout.flush()
    
    if delete_input:
      os.remove(file)
      print '\r loaded %s, words: %s *deleted* ' % (filename(file).rjust(rjust), format(words_in_file + words_created, ',d').rjust(njust)),
      sys.stdout.flush()
  
  # at this point, we are done extracting data from the list of input files
  
  if files_loaded == 0:
    print '\n no files found! exiting'
    sys.exit(0)
    
  # check if there are still items left in the chunk to be saved
  if len(lst) > 0:
    print '\r loaded %s, words: %s *sorting*' % (filename(file).rjust(rjust), format(words_in_file + words_created, ',d').rjust(njust)),
    sys.stdout.flush()
    
    if not still_sorted: # the list is not already sorted
      lst.sort()         # sort the chunk
    
    print '\r loaded %s, words: %s *chunking*' % (filename(file).rjust(rjust), format(words_in_file + words_created, ',d').rjust(njust)),
    sys.stdout.flush()
    
    o = open(temp_dir + str(split_file), 'wb')
    o.write('\n'.join(lst)) # save the chunk
    o.close()
    
    del lst[:]
    split_file += 1
    print '\r loaded %s, words: %s            ' % (filename(file).rjust(rjust), format(words_in_file + words_created, ',d').rjust(njust)),
    sys.stdout.flush()
    
    if delete_input:
      print '\r loaded %s, words: %s *deleted* ' % (filename(file).rjust(rjust), format(words_in_file + words_created, ',d').rjust(njust)),
      sys.stdout.flush()
      
  print '\n        ' + ('%d files' % (files_loaded)).rjust(rjust) + ', total: %s words' % (format(words_kept + words_created, ',d')).rjust(njust)
  
  result = []
  for x in xrange(0, split_file):
    result.append(temp_dir + str(x))
  
  return result # return list of filenames containing the sorted chunks

# generator for lines in a file. used by the 'merge' function
def file_gen(file):
  f = open(file, 'rb')
  line = f.readline()
  while line:
    yield line
    line = f.readline()
    
  f.close()
  os.remove(file)

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Merge
Result: all data contained in 'chunks' is saved to 'file',
        maintaining sorted order'file',
        size will not exceed split_size (bytes)
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def merge(chunks, file):
  global words_removed_duplicates
  
  outfile = open(file, 'wb')
  
  saving_to = file # current file we are writing to (subject to change as size exceeds split_size)
  
  bytes_so_far, bytes_cur, count, split_file = 0, 0, 0, 0 # counters for bytes/lines
  
  # total number of bytes for all input files
  bytes_ttl = sum(os.path.getsize(str(chunk)) for chunk in chunks)
  
  words_in_file, words_kept, last = 0, 0, '' # word counters
  
  # frequency counters
  freq_count, freq_list = 1, []
  
  # it will take our input files and grab the next-smallest word from each file!
  for line in heapq.merge(*(file_gen(f) for f in chunks)):
    
    if freq_flag:
      print '\r counting words: %s (%.3f%%)' % (format(words_in_file, ',d').rjust(njust), 100 * float(bytes_cur) / float(bytes_ttl)),
      sys.stdout.flush()
    else:
      print '\r saving ' + filename(saving_to).rjust(rjust) + ', words: %s (%.3f%%)' % (format(words_in_file, ',d').rjust(njust), 100 * float(bytes_cur) / float(bytes_ttl)),
      sys.stdout.flush()
    
    bytes_cur += len(line)
    
    if bytes_so_far + len(line) >= split_size:
      outfile.close()
      print '\r saved  ' + filename(saving_to).rjust(rjust) + ', words: %s (%s)      ' % (format(words_in_file, ',d').rjust(njust), inttosize(bytes_so_far))
      split_file += 1
      c = file.rfind('.')
      if c == -1: c = len(file) - 1
      saving_to = file[:c] + '-' + str(split_file) + '' + file[c:]
      outfile = open(saving_to, 'wb')
      words_in_file = 0
      bytes_so_far = 0
    
    if not remove_duplicates or line != last:
      
      if freq_flag:
        if freq_count >= freq_min:
          freq_list.append((freq_count, last))
        
        # ensure the sorted list is not too big
        if sys.getsizeof(freq_list) > chunk_size:
          freq_list.sort(reverse=True) # reverse sort
          while sys.getsizeof(freq_list) > chunk_size:
            freq_list.pop(len(freq_list) - 1) # remove least-frequently-occuring element.
        freq_count = 1
      else:
        outfile.write(line)
        bytes_so_far += len(line)
        
      last = line
      words_in_file += 1
      words_kept += 1
    
    elif freq_flag:
      freq_count += 1
      pass
      
    else:
      words_removed_duplicates += 1
      
    count += 1

# extract the filename from a path
def filename(path):
  s = path.rfind(os.sep)
  if s == -1:
    result = path
  else:
    result = path[s+1:]
  
  if len(result) < rjust:
    return result
  mid = int(rjust / 2)
  return result[:mid-1] + '...' + result[2+len(result)-mid:]

# converts string representation of a filesize to int (bytse)
# ex: sizetoint('1mb') returns 1048576
def sizetoint(size):
  snum = ''
  for char in size:
    if char.isdigit() or char == '.': 
      snum += char
    else:
      break
  num = float(snum)
  
  chars = size[len(snum):].strip().lower()
  chars = chars.replace('b','')
  if chars == 't':
    num = num * 1024 * 1024 * 1024 * 1024
  elif chars == 'g':
    num = num * 1024 * 1024 * 1024
  elif chars == 'm':
    num = num * 1024 * 1024
  elif chars == 'k':
    num = num * 1024
  
  return int(num)

# converts numeric bytes into human-readable format
def inttosize(bytes):
  b = 1024 * 1024 * 1024 * 1024
  a = ['t','g','m','k','']
  for i in a:
    if bytes >= b:
      return '%.2f%sb' % (float(bytes) / float(b), i)
    b /= 1024
  return '0b'

# converts seconds to human-readable format
# ex: sectotime(3661) returns '1h 1m 1.00s'
def sectotime(sec):
  result = ''
  
  if sec > 3600:
    result = '%dh ' % (sec / 3600)
  
  sec %= 3600
  if sec > 60:
    result += '%dm ' % (sec / 60)
  
  sec %= 60
  result += str('%.2fs' % sec)
  
  return result

# print help screen
def help():
  print ' this script sorts wordlists.'
  print "   -o $       output file sorted data is written to. default: sorted.dat"
  print "   -c #       chunk size. this decides how much data is loaded into memory"
  print "   -d         do NOT remove duplicates. default: remove duplicate lines"
  print "              ex: -s 100mb splits output into 100 megabyte chunks"
  print ' usage: python sorter.py [FILE(S)]'

# return path to this file (sorter.py)
def get_script_path():
  p = os.path.realpath(__file__)
  p = p[:p.rfind(os.sep)+1]
  return p

# parse command-line arguments, set global variables
def parse_args(args):
  global remove_duplicates
  global split_size, chunk_size, outfile
  global strip_whitespace
  global freq_flag, freq_show_count, delete_input
  
  result, i = [], 0
  
  printed = False
  
  while i < len(args):
    x = args[i]

    if x == '-o' or x == '--output':
      if i == len(args) - 1:
        print ' output file name required!'
        sys.exit(0)
      outfile = args[i+1]
      print ' * output file set: "' + outfile + '"'
      i += 1
      
    elif x == '-d' or x == '--duplicates':
      remove_duplicates = False
      printed = True
      print ' * duplicate removal disabled'
      
    elif x == '-s' or x == '--split':
      if i == len(args) - 1:
        print ' split size (in bytes) required!'
        sys.exit(0)
      split_size = sizetoint(args[i+1])
      printed = True
      print ' * file split size set: ' + format(split_size, ',d') + ' bytes'
      i += 1
      
    elif x == '-c' or x == '--chunk':
      if i == len(args) - 1:
        print ' chunk size (in bytes) required!'
        sys.exit(0)
      chunk_size = sizetoint(args[i+1])
      printed = True
      print ' * chunk size set:', format(chunk_size, ',d'), 'bytes'
      i += 1

    elif x == '-help' or x == '/?' or x == '--help' or x == '-h' or x == '?':
      help()
      sys.exit(0)

    elif x == '-w' or x == '--no-strip':
      strip_whitespace = False
      print ' * whitespace stripping disabled'
      printed = True
      
    elif x == '-freq' or x == '--freq':
      freq_flag = True
      freq_show_count = False
      print ' * sorting by frequency enabled'
      printed = True
      
    elif x == '-freqn' or x == '--freq-count':
      freq_flag = True
      freq_show_count = True
      print ' * sorting by frequency enabled, line frequency is included in output'
      printed = True
      
    elif x == '-kill' or x == '--delete-input-files':
      delete_input = True
      
    elif x == '-lower' or x =='-lcase':
      copy_lower = True
      print ' * lower-case copies enabled'
      printed = True
      
    elif x == '-upper' or x =='-ucase':
      copy_upper = True
      print ' * upper-case copies enabled'
      printed = True
      
    elif x == '-first' or x =='--first':
      copy_first = True
      print ' * first-letter-upper copies enabled'
      printed = True
      
    elif x == '-elite' or x == '--elite':
      copy_elite = True
      print ' * elite (leetspeak) mutations enabled'
      printed = True
      
    else:
      if x.find('*') != -1:
        fixed = ''
        for letter in x:
          if letter == '[':
            fixed += '[[]'
          elif letter == ']':
            fixed += '[]]'
          else:
            fixed += letter
        x = fixed
        for item in glob(x):
          result.append(item)
          
      elif os.path.isfile(x):
        result.append(x)
        
      elif os.path.isdir(x):
        if not x.endswith(os.sep):
          x += os.sep
        for item in glob(x + '*'):
          result.append(item)
    i += 1
  
  if printed: print ''
  
  return result

# where the magic happens!
def start(args):
  global outfile, words_removed_duplicates
  print ""
  print " / sorting has begun /"
  print ""
  
  files = parse_args(args)
  if len(files) == 0:
    help()
    print '\n no input files given!'
    sys.exit(0)
  
  before = time.time()
  chunks = split(files)
  print ''
  merge(chunks, outfile)
  print '\n finished in %s' % (sectotime(time.time() - before))
  
  if words_removed_duplicates > 0:
    print '\n removal statistics:'
    times = 0
      
    if words_removed_duplicates > 0:
      print '   * duplicates:%s words' % (format(words_removed_duplicates,  ',d').rjust(njust))
      times += 1

    if times > 1:
      print '                 ------------------'
      print '   * total rm\'d:%s words' % (format(words_removed_duplicates, ',d').rjust(njust))

if __name__ == '__main__':
  
  try:
    start(sys.argv[1:])
    
  except KeyboardInterrupt:
    print '\n\n^C interrupt, exiting'
    
  except SystemExit:
    pass
    
  except:
    s = sys.exc_info()
    for e in s:
      print "ERROR: " + str(e)
  
  # remove temporary files
  i = 0
  while os.path.exists(temp_dir + str(i)):
    os.remove(temp_dir + str(i))
    i += 1
  os.rmdir(temp_dir)
  
  print '\n *** press enter to exit ***'
  raw_input()
