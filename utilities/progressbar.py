class ProgressBar:
    def __init__ (self, iteration, limit, prefix, suffix, fill='█', length = 50):
        self.prefix = prefix
        self.bar = fill * int(length * iteration // limit) + '-' * (length - int(length * iteration // limit))
        self.percent = ("{0:.1f}").format(100 * (iteration / float(limit)))
        self.suffix = suffix

    def print (self):
        """
        Print the progress bar
        """
        print(f'\r{self.prefix} |{self.bar}| {self.percent}% {self.suffix}', end='', flush=True)
