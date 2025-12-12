import time

class Time:
    def __init__(self, minutes=0, seconds=0):
        self.minutes = minutes
        self.seconds = seconds

    def __str__(self):
        return f"{self.minutes} minutes and {self.seconds} seconds"
    
    def print(self):
        print(f"Elapsed time: {self.minutes} minutes and {self.seconds} seconds")

class Timer:
    def __init__(self, name: str = "Timer", runtime: Time = None):
        self.name = name
        self.runtime = runtime

        self.start_time = None
        self.end_time = None

    def start(self):
        self.start_time = time.time()

    def stop(self):
        self.end_time = time.time()
        self.runtime_adjust()

    def elapsed(self):
        if self.start_time is None or self.end_time is None:
            raise ValueError("Timer has not been started and stopped properly.")
        return self.end_time - self.start_time
    
    # Runtime
    def runtime_adjust(self):
        elapsed_time = self.elapsed()
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        self.runtime = Time(minutes, seconds)
    
    # __str__: method to print Timer info
    def __str__(self):
        return f"{self.name} - {self.runtime}"
    