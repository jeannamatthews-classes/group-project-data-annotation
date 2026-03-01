class Span:
    """Stores info pertinent to spans of intrest
       span_length (int): amount of time that span spans in milliseconds 
    """
    def __init__(self, start: int, stop: int):
        """instantiates a Span object
            start (int): time a span starts in milliseconds from beginning 
            stop (int): time a span ends in milliseconds from beginning
        """
        self.start = start
        self.stop = stop
        self.span_length = self.stop - self.start

    def __str__(self):
        return(f"{self.start} to {self.stop}")

    def get_start(self) -> int:
        return self.start
    def get_stop(self) -> int:
        return self.stop


