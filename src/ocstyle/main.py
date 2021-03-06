#!/usr/bin/env python
# Copyright 2012 The ocstyle Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Basic Objective C style checker."""

import argparse
import os.path
import sys

import parcon
import fnmatch
import os
import pdb
import json

from ocstyle import rules

def isExcluded(base, testDir, excDirs):
  exc = False
  for excDir in excDirs:
    fullPathExc = base + excDir
    if fullPathExc in testDir:
      exc = True
      break
  return exc

def getFileList(base, excDirs):
  matches = []
  for root, dirnames, filenames in os.walk(base):
    if not isExcluded(base, root, excDirs):
      for filename in filenames:
        if filename.endswith(('.m', '.mm', '.h')):
          matches.append(os.path.join(root, filename))
  return matches

def check(path, maxLineLength):
  """Style checks the given path."""
  with open(path) as f:
    return checkFile(path, f, maxLineLength)


def removeMainDir(mainDir, filepath):
  if mainDir.endswith('/'):
    removePath = mainDir
  else:
    removePath = mainDir + '/'
  return filepath.replace(removePath, '')

def checkFile(path, f, maxLineLength):
  """Style checks the given file object."""
  content = f.read()
  lineErrors = rules.setupLines(content, maxLineLength)
  result = parcon.Exact(rules.entireFile).parse_string(content)
  if path.endswith(('.m', '.mm')):
    result = [err for err in result if not isinstance(err, rules.Error) or not err.kind.endswith('InHeader')]
  result.extend(lineErrors)
  result.sort(key=lambda err: err.position if isinstance(err, rules.Error) else 0)
  return result


def main():
  """Main body of the script."""

  parser = argparse.ArgumentParser()
  parser.add_argument("--maxLineLength", action="store", type=int, default=120, help="Maximum line length")
  parser.add_argument("--excludedDirs", action="store", default='/Core/Frameworks', help="Directores to exclude from linting")
  args, dirs = parser.parse_known_args()
  if len(dirs) == 0:
    print "Please add at least one directory as an argument."
    exit()
  excludedDirs = args.excludedDirs.split(',')
  mainDir = dirs[0]
  filenames = getFileList(mainDir, excludedDirs)
  errors = {}
  errors["violations"] = []
  for filename in filenames:
    if not os.path.isdir(filename):
    #   print filename
      try:
        for part in check(filename, args.maxLineLength):
          if isinstance(part, rules.Error):
            errors["violations"].append({'file': removeMainDir(mainDir, filename),
                                       'line': part.lineAndOffset()[0],
                                       'type': part.kind,
                                       'error': part.kind + " - " + part.message})
      except:
        pass
  print json.dumps(errors, indent=4, separators=(',', ': '))

if __name__ == '__main__':
  main()
