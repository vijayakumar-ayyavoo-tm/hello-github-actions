#!/usr/bin/env python
import os, sys, re

def readFileContents(filePath):
  contents=''
  # Open the file as f.
  # The function readlines() reads the file.             
  with open(filePath) as f:
      content = f.readlines()
   
  for line in content:
    if line.strip() != '':
      contents+=line.rstrip()
  return contents

def filterBranchNames(branches, pattern):
  filteredBranches=[]
  for branch in branches:
    if (re.search(pattern, branch)):
      # print(branch)
      filteredBranches.append(branch)
  return filteredBranches

def listNormalizedBranches(pathprefix, branches):
  normalizedBranches=[]
  for branch in branches:
    if (branch.startswith('feature')) or (branch.startswith('release')) or (branch.startswith('bugfix')) or (branch.startswith('hotfix')):
      normalizedBranches.extend(iterateFolders(pathprefix, branch))
    else:
      normalizedBranches.append(branch)
  return normalizedBranches

def iterateFolders(pathprefix, branchType):
  files=[]
  filesinfolder=os.listdir(pathprefix+'.git/refs/remotes/origin/' + branchType + '/')
  for temp in filesinfolder:
    files.append(branchType + '/' + temp)
  return files

def readRemoteBranches(filePath):
  branches=[]
  with open(filePath) as f:
      content = f.readlines()
   
  for line in content:
    if "refs/remotes/" in line: 
      remotebranch=line[line.rfind('refs/remotes/')+20:]
      if remotebranch.strip() != '':
        branches.append(remotebranch.rstrip())
  return branches

def readRemoteTags(filePath):
  tags=[]
  with open(filePath) as f:
      content = f.readlines()
   
  for line in content:
    if "refs/tags/" in line: 
      remotetag=line[line.rfind('refs/tags/')+10:]
      if remotetag.strip() != '':
        tags.append(remotetag.rstrip())
  return tags

def getMaxReleaseVersion(relBranches):
  major=0
  minor=0
  for branch in relBranches:
    branchVer=branch[branch.find('/')+1:]
    branchMajor=int(branchVer[:branchVer.find('.')])
    branchMinor=int(branchVer[branchVer.find('.')+1:])
    if branchMajor == major:
      if branchMinor > minor:
        major = branchMajor
        minor = branchMinor
    if branchMajor > major:
      major = branchMajor
      minor = branchMinor
  return str(major)+'.'+str(minor)

def filterTags(tags, pattern):
  filteredtags=[]
  for tag in tags:
    if tag.find(pattern) > -1:
      filteredtags.append(tag)
  return filteredtags
