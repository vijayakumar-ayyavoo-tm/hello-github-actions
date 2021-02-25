#!/usr/bin/env python

import os, sys, gitmodules, re

# Valid version tags to be considered
versionPattern = '^[0-9]+[.][0-9]+[.][0-9]+$|[0-9]+[.][0-9]+[.][0-9]+[-](develop.)[0-9]+$|[0-9]+[.][0-9]+[.][0-9]+[-](rc.)[0-9]+$'
# Valid release branch name pattern
releaseBranchPattern = '^(release/)[0-9]+[.][0-9]+$'

argsLength = len(sys.argv)
prefix = ''
if argsLength > 1:
    prefix = sys.argv[1]


class Version:
    def __init__(self, versionStr):
        verArr = versionStr.split('.')
        self.major = int(verArr[0])
        self.minor = int(verArr[1])
        if len(verArr) > 3:
            patchStr = verArr[2] + '.' + verArr[3]
            if patchStr.find('-') != -1:
                self.patch = int(patchStr[:patchStr.find('-')])
                self.suffix = patchStr[patchStr.find('-') +
                                       1:patchStr.rfind('.')]
                self.suffixversion = int(patchStr[patchStr.rfind('.') + 1:])
            else:
                self.patch = int(patchStr)
                self.suffix = ''
        elif len(verArr) == 3:
            self.patch = int(verArr[2])
            self.suffix = ''

    def __str__(self):
        strrepesentation = '{major}.{minor}'.format(
            major=self.major, minor=self.minor)
        if hasattr(self, 'patch'):
            strrepesentation = strrepesentation + '.{patch}'.format(
                patch=self.patch)
        if hasattr(self, 'suffix'):
            strrepesentation = strrepesentation + '-{suffix}'.format(
                suffix=self.suffix)
        if hasattr(self, 'suffixversion'):
            strrepesentation = strrepesentation + '.{suffixversion}'.format(
                suffixversion=self.suffixversion)
        return strrepesentation

    def bumpMajor(self):
        self.major = self.major + 1

    def bumpMinor(self):
        self.minor = self.minor + 1

    def bumpPatch(self):
        if hasattr(self, 'patch'):
            self.patch = self.patch + 1
        else:
            self.patch = 0

    def bumpSuffixVersion(self):
        self.suffixversion = self.suffixversion + 1


def fetchHighestSuffixVersion(major, minor, patch, suffix, tags):
    suffixversion = 0
    for tag in tags:
        if (re.search(versionPattern, tag)):
            v = Version(tag)
            if int(major) == int(v.major) and int(minor) == int(
                    v.minor) and int(patch) == int(
                        v.patch) and suffix == v.suffix:
                suffixversion = int(
                    v.suffixversion
                ) if v.suffixversion > suffixversion else suffixversion
    return suffixversion + 1


def filterReleasedTags(tags):
    filteredtags = []
    for tag in tags:
        if (re.search(versionPattern, tag)):
            v = Version(tag)
            if not v.suffix:
                filteredtags.append(tag)
    return filteredtags


def fetch_patch_number(major, minor, release_tags, rc_tags):
    max_patch_from_release = -1
    max_patch_from_rc = -1
    patch = None
    for tag in release_tags:
        if (re.search(versionPattern, tag)):
            v = Version(tag)
            if int(major) == int(v.major) and int(minor) == int(v.minor):
                max_patch_from_release = int(
                    v.patch
                ) if v.patch > max_patch_from_release else max_patch_from_release
    for tag in rc_tags:
        if (re.search(versionPattern, tag)):
            v = Version(tag)
            if int(major) == int(v.major) and int(minor) == int(v.minor):
                max_patch_from_rc = int(
                    v.patch
                ) if v.patch > max_patch_from_rc else max_patch_from_rc
    if max_patch_from_release == -1 and max_patch_from_rc == -1:
        patch = 0
    elif max_patch_from_release >= max_patch_from_rc:
        patch = max_patch_from_release + 1
    elif max_patch_from_rc > max_patch_from_release:
        patch = max_patch_from_rc
    return patch


try:
    branches = gitmodules.readRemoteBranches(prefix + '.git/packed-refs')
    branchref = gitmodules.readFileContents(prefix + '.git/HEAD')
    currentbranch = branchref[branchref.rfind('heads/') + 6:]
    tags = gitmodules.readRemoteTags(prefix + '.git/packed-refs')
    releasebranches = gitmodules.filterBranchNames(branches,
                                                   releaseBranchPattern)
    # featurebranches=gitmodules.filterBranchNames(branches, 'feature')
    # bugfixbranches=gitmodules.filterBranchNames(branches, 'bugfix')
    # hotfixbranches=gitmodules.filterBranchNames(branches, 'hotfix')
    # For develop/feature/bugfix and hotfix branches
    if currentbranch == 'develop' or currentbranch.startswith(
            'feature') or currentbranch.startswith(
                'bugfix') or currentbranch.startswith('hotfix'):
        # If no tags and releases, start with 0.1.0
        major = 0
        minor = 1
        patch = 0
        suffix = 'develop' if currentbranch == 'develop' else currentbranch.replace(
            '/', '-')
        suffixversion = 1  # Should it be the CI Build# ? It wont reset to 1 after bumping up minor version
        if len(releasebranches) > 0:
            maxreleaseversion = Version(
                gitmodules.getMaxReleaseVersion(releasebranches))
            maxreleaseversion.bumpMinor()
            maxreleaseversion.bumpPatch()
            major = maxreleaseversion.major
            minor = maxreleaseversion.minor
            patch = maxreleaseversion.patch
        # If tags are present for develop, use it to bump up suffixversion
        if currentbranch == 'develop':
            developtags = gitmodules.filterTags(tags, '-develop.')
            if len(developtags) > 0:
                suffixversion = fetchHighestSuffixVersion(
                    major, minor, patch, suffix, developtags)
        else:
            # For feature, bugfix and hotfix create mutable version (overwrite previous version in the branch)
            # suffixversion=os.environ['BUILD_NUMBER']
            suffixversion = 1
        calculatedVersion = Version(
            str(major) + '.' + str(minor) + '.' + str(patch) + '-' + suffix +
            '.' + str(suffixversion))
        print(str(calculatedVersion))

    # For release branch
    if currentbranch.startswith('release'):
        # If no tags, start with $releasename+.0
        major = currentbranch[currentbranch.find('/') +
                              1:currentbranch.find('.')]
        minor = currentbranch[currentbranch.find('.') + 1:]
        patch = 0
        suffix = 'rc'
        suffixversion = 1
        # Get released tags
        releasetags = filterReleasedTags(tags)
        rctags = gitmodules.filterTags(tags, '-rc.')
        if len(rctags) > 0:
            patch = fetch_patch_number(major, minor, releasetags, rctags)
            suffixversion = fetchHighestSuffixVersion(major, minor, patch,
                                                      suffix, rctags)
        calculatedVersion = Version(
            str(major) + '.' + str(minor) + '.' + str(patch) + '-' + suffix +
            '.' + str(suffixversion))
        print(str(calculatedVersion))
except Exception as e:
    print("Exception calculating version")
    raise
