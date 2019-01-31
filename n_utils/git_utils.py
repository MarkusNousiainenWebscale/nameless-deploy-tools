from builtins import object
import re
import shutil
import tarfile
import tempfile
from os import environ, devnull, linesep
from subprocess import Popen, PIPE
from locale import getpreferredencoding

SYS_ENCODING = getpreferredencoding()

class Git(object):

    def __init__(self):
        self.entered = 0
        self.export_directories = {}
        self.current_branch = None
        self.branches = []
        self.root = None

    def __enter__(self):
        self.entered += 1
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.entered -= 1
        if self.entered == 0:
            self.delete_exports()
        return None

    def _get_export_directory(self, branch):
        if branch in self.export_directories:
            return self.export_directories[branch]
        else:
            co_dir = tempfile.mkdtemp()
            self.export_directories[branch] = co_dir
            return co_dir
    
    def _resolve_branch(self, branch):
        proc = Popen(["git", "branch", "-a"], stdout=PIPE)
        output, _ = proc.communicate()
        if proc.returncode == 0:
            for line in output.decode(SYS_ENCODING).split(linesep):
                line = re.sub(r"^[\*\s]*", "", line).strip()
                if "origin/HEAD" in line:
                    continue
                if line.endswith("origin/" + branch) or line == branch:
                    return line.split(" ")[-1:][0]
        return None

    def delete_exports(self):
        for dir in list(self.export_directories.values()):
            try:
                shutil.rmtree(dir)
            except:
                # Best effport deleting only - not fatal
                pass

    def export_branch(self, branch):
        if branch == self.get_current_branch():
            return self.get_git_root()
        with self:
            try:
                checkout_dir = self._get_export_directory(branch)
                export_branch = self._resolve_branch(branch)
                if not export_branch:
                    raise CheckoutException("Failed to resolve branch " + branch + " for export")
                proc = Popen(["git", "archive", "--format", "tar", export_branch], stdout=PIPE, stderr=open(devnull, 'w'))
                tar = tarfile.open(mode="r|", fileobj=proc.stdout)
                tar.extractall(path=checkout_dir)
            except tarfile.ReadError:
                raise CheckoutException("Failed to export branch " + branch)
            return checkout_dir

    def get_git_root(self):
        if not self.root:
            proc = Popen(["git", "rev-parse", "--show-toplevel"], stdout=PIPE, stderr=open(devnull, 'w'))
            stdout, _ = proc.communicate()
            if proc.returncode == 0:
                self.root = stdout.decode(SYS_ENCODING).strip()
            else:
                self.root = "."
        return self.root

    def get_branches(self):
        if not self.branches:
            proc = Popen(["git", "branch", "-a"], stdout=PIPE, stderr=open(devnull, 'w'))
            output, _ = proc.communicate()
            for line in output.decode(SYS_ENCODING).split(linesep):
                line = re.sub(r"^[\*\s]*", "", line).strip()
                if not line:
                    continue
                if "origin/HEAD" in line:
                    continue
                branch = line.split(" ")[-1:][0]
                if branch:
                    branch = branch.split("origin/")[-1:][0]
                if branch not in self.branches:
                    self.branches.append(branch)
        return self.branches

    def get_current_branch(self):
        if not self.current_branch:
            if "GIT_BRANCH" in environ:
                self.current_branch = environ["GIT_BRANCH"]
            else:
                proc = Popen(["git", "rev-parse", "--abbrev-ref", "HEAD"], stdout=PIPE, stderr=open(devnull, 'w'))
                stdout, _ = proc.communicate()
                if proc.returncode == 0:
                    self.current_branch = stdout.decode(SYS_ENCODING).strip()
                else:
                    self.current_branch = "master"
            self.current_branch = self.current_branch.split("/")[-1:][0]
        return self.current_branch


class CheckoutException(Exception):
    pass