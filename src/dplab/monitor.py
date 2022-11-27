# reference to: https://stackoverflow.com/questions/13607391/subprocess-memory-usage-in-python

import time
import psutil
import subprocess
import tracemalloc


class MonitoredProcess:
    def __init__(self, command):
        self.command = command
        self.executed = False
    
    def is_running(self):
        return psutil.pid_exists(self.p.pid) and self.p.poll() == None
    
    def check_execution_state(self):
        if not self.executed:
            return False
        if self.is_running():
            return True
        self.executed = False
        self.t1 = time.time()
        return False

    def execute(self):
        self.vms_memory_seq = []
        self.rss_memory_seq = []

        self.t0 = time.time()
        self.t1 = None
        self.p = subprocess.Popen(self.command, shell=False)
        self.executed = True

    def poll(self):
        if not self.check_execution_state():
            return False
        self.t1 = time.time()
        try:
            pp = psutil.Process(self.p.pid)
            #obtain a list of the subprocess and all its descendants
            descendants = [pp, *list(pp.children(recursive=True))]
            rss_memory = 0
            vms_memory = 0
            for descendant in descendants:
                try:
                    mem_info = descendant.memory_info()
                    rss_memory += mem_info[0]
                    vms_memory += mem_info[1]
                except psutil.NoSuchProcess as e:
                    #sometimes a subprocess descendant will have terminated between the time
                    # we obtain a list of descendants, and the time we actually poll this
                    # descendant's memory usage.
                    pass
            self.vms_memory_seq.append(vms_memory)
            self.rss_memory_seq.append(rss_memory)
        except psutil.NoSuchProcess:
            pass
        return self.check_execution_state()
    
    def close(self, kill=False):
        try:
            pp = psutil.Process(self.p.pid)
            if kill:
                pp.kill()
            else:
                pp.terminate()
        except psutil.NoSuchProcess:
            pass

def measure_command_workload(command, interval=0.1):
    mp = MonitoredProcess(command)
    try:
        mp.execute()
        while mp.poll():
            time.sleep(interval)
    finally:
        mp.close()
    return {
        "time": mp.t1 - mp.t0,
        "peak_vms_memory": max(mp.vms_memory_seq, default=0),
        "peak_rss_memory": max(mp.rss_memory_seq, default=0),
        "_vms_memory_seq": mp.vms_memory_seq,
        "_rss_memory_seq": mp.rss_memory_seq,
    }

def measure_func_workload(func, args):
    tracemalloc.start()
    try:
        time_start = time.time()
        func_result = func(**args)
    except Exception as e:
        func_result = RuntimeError(f"Error while measuring function workload: {e}")
    finally:
        time_end = time.time()
        memory_final, memory_peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        return func_result, {
            "internal_time": time_end - time_start,  # unit: second
            "internal_memory_final": memory_final,  # unit: byte
            "internal_memory_peak": memory_peak,
        }


if __name__ == "__main__":
    PYTHON_COMMAND = "python3"
    print(measure_command_workload([PYTHON_COMMAND, '-c', 'import time; time.sleep(3)']))
    def sleep_3s():
        time.sleep(3)
    print(measure_func_workload(sleep_3s, {})[1])
