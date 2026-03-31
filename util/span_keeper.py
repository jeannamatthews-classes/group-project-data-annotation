from util.span_class import Span
from pathlib import Path

class SpanKeeper:
    """Handles adding and organization of individual Span objects
        start_temp (int | None): marker for storing start time of span being added 
    """
    def __init__(self, spans_to_load: Path | None = None):
        """Instantiates a SpanKeeper object
            spans_to_load optional(Path): specifies location to load Spans from
        """
        if spans_to_load is not None:
            self.spans: list[Span] = [] # Some sort of loading for spans
        else:
            self.spans: list[Span] = []
        
        self.start_temp: int | None = None

    def __getitem__(self, idx: int) -> tuple[int, int]:
        span = self.spans[idx]
        return (span.get_start(), span.get_stop())
    
    def get_spans(self) -> list[Span]:
        return self.spans
    def is_start_set(self) -> bool:
        return bool(self.start_temp)

    def span_mark(self, timestamp: int) -> bool:
        if self.start_temp is None:
            self.start_temp = timestamp
            return True
        else:
            self.spans.append(Span(self.start_temp, timestamp))
            self.start_temp = None
            return False