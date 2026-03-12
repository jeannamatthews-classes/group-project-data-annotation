import csv

class DataReader:
    """
    csv wrapper class to parse rows of sensor data sequentially.
    """
    def __init__(self, filepath: str):
        self._success: bool = False

        try:
            self._file = open(filepath, newline="", encoding="utf-8")
            self._reader = csv.reader(self._file, quoting=csv.QUOTE_NONNUMERIC)
            self._success = True
            self._init_data_info()
        except:
            return

    def __del__(self):
        if self._success:
            self._file.close()

    def _init_data_info(self):
        # Columns for our data: ax, ay, az, gx, gy, gy, mx, my, mz, qw, qx, qy, qz, sync_ts, per_sampls_ts

        self._time_idx = 14 # TODO: generalize for other kinds of data; find which column only increases
        self._columns = len(self.next_row())
        # TODO: data range, column ranges for each sensor?
        # find seek points here?

        self.reset()

    @property
    def success(self):
        return self._success

    @property
    def time_idx(self):
        return self._time_idx

    @property
    def columns(self):
        return self._columns

    def next_row(self) -> list[str]:
        try:
            return self._reader.__next__()
        except:
            return None

    def reset(self):
        if self._success:
            self._file.seek(0)