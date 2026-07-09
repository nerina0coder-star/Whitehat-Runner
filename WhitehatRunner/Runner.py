import subprocess
import time
from pathlib import Path

import psutil
import re2
from typeguard import typechecked

from .ASTSecure import ASTSecure
from .Whitelist import Whitelist
import subprocess
import time
from pathlib import Path

import psutil
import re2

from .ASTSecure import ASTSecure
from .Whitelist import Whitelist


class Runner:
    """
    The class that extracts and runs code from the given input.
    """

    @typechecked
    def __init__(self, whitelist: Whitelist, max_workers: int | None = None):
        """Accepts a whitelist class for accepting/denying user input"""
        self.whitelist = whitelist
        self.__secure__ = ASTSecure(whitelist, max_workers)
    #def __getattr__(self, name):
    # Found out what it does, python is truly not secure.
    # Well, then please be moral and don't touch these for your own sake.

    @typechecked
    def __getcode(self, txt: str):
        """Extracts and returns the embedded code."""
        pattern = re2.compile(r'\[start\[.*?\]end\]')
        matches = pattern.findall(txt)
        lst = list(matches) if matches is not None else None
        out = None
        if lst is not None:
            out = [i[7:-5].strip().replace(r'\[start\[', '[start[').replace(r'\]end\]', ']end]') for i in lst]
        return out

    @typechecked
    def __base_run(self, path: str|None, raw: str|None):
        self.__secure__.reset()
        if path is None and raw is None:
            raise ValueError('Both path and raw are None.')
        if path is not None and not Path(path).exists():
            raise FileNotFoundError(f'The file at path {path} doesn\'t exist')
        txt = raw if raw is not None else open(path, 'r').read().strip()
        splitted = txt.splitlines()
        # Extracting
        codes = []
        for i in splitted:
            c = self.__getcode(i)
            if c is not None:
                codes.extend(c)
        # Keeping it clean.
        splitted.clear()
        txt = ""

        del splitted
        del txt
        return codes

    @typechecked
    def runny(self, path: str | None = None, raw: str | None = None):
        """Writes to a file and extracts the code that's inside a file/string.
        Args:
             path(str): A path to the file to read.
             raw(str): Raw string to extract code from.
        Raises:
            ValueError: Both path and raw are None.
            FileNotFoundError: File at path doesn't exist.
            RuntimeError: An error occurred when running x: error
            RuntimeError: Call x is prohibited.
        """
        # code
        codes = self.__base_run(path, raw)

        # Executing
        try:
            isSafe = self.__secure__(codes)
            # check(code) and
            if isSafe:
                for code in codes:
                    yield lambda doeval: exec(code, self.whitelist.whitelisted_globals) if not doeval else eval(code, self.whitelist.whitelisted_globals)
            else:
                raise RuntimeError(f'Call is prohibited')
        except Exception as e:
            raise RuntimeError(f'An error acquired when running:\n{str(e)}')

    @typechecked
    def runner(self, path: str | None = None, raw: str | None = None,
               output_path: str | None = None, max_cpu: int | None = None,
               max_cpu_cores: int | None = None, max_ram: int | None = None):
        """Writes to a file and extracts the code that's inside a file/string.
        Args:
             path(str): A path to the file to read.
             raw(str): Raw string to extract code from.
             output_path(str): A path to the file to write the code to.
             max_cpu(int): Maximum seconds of CPU to use when running the code.
             max_ram(int): Maximum RAM to use in MegaBytes when running the code.
             max_cpu_cores(int): Maximum number of CPU cores to use.
        Raises:
            ValueError: Both path and raw are None.
            FileNotFoundError: File at path doesn't exist.
            RuntimeError: An error occurred when running x: error
            RuntimeError: Call x is prohibited.
        """
        # Correcting user input
        if output_path is not None and not Path(output_path).parent.exists():
            raise FileNotFoundError(f'The output path does not exist {output_path} doesn\'t exist')
        # Output
        output = None
        out = ""
        max_cpu_percentage = 0
        
        output = open(output_path, 'w')
        if max_cpu is None or max_ram is None or max_cpu_cores is None:
            raise ValueError(
               'Either/all max_cpu or max_ram or max_cpu_cores are None when using rumner.'
               )
        max_cpu_percentage = max_cpu_cores * 100
        codes = self.__base_run(path, raw)
        # Validation
        try:
            isSafe = self.__secure__(codes)
            # check(code) and
            if isSafe:
                out = "".join(f"{code}\n" for code in codes)
            else:
                raise RuntimeError(f'Call is prohibited')
        except Exception as e:
            raise RuntimeError(f'An error acquired when running:\n{str(e)}')
        output.write(out)
        output.flush()
        output.close()
        proc = subprocess.Popen(["python", output_path])
        p = psutil.Process(proc.pid)
        try:
            while p.is_running():
                all_proc = [p] + p.children(recursive=True)

                cpu_times = 0
                cpu_percentage = 0
                for i in all_proc:
                    try:
                        times = i.cpu_times()
                        cpu_times += times.user + times.system
                        cpu_percentage += i.cpu_percent(interval=5)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                if cpu_times > max_cpu or cpu_percentage > max_cpu_percentage:
                    self.__killproc(all_proc)
                    break


                ram_usage = 0
                for i in all_proc:
                    try:
                        ram_usage += i.memory_info().rss
                    except psutil.NoSuchProcess:
                        pass
                ram_usage = ram_usage / (1024 * 1024)
                if ram_usage > max_ram:
                    self.__killproc(all_proc)
                    break
                if not p.is_running():
                    break
                time.sleep(1)
        except psutil.NoSuchProcess:
            pass
        return

    def __killproc(self, procs):
        for i in procs:
            try:
                i.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        gone, alive = psutil.wait_procs(procs, timeout=3)
        for j in alive:
            try:
                j.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

            # TODO
