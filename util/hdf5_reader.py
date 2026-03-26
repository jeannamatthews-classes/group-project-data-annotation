import h5py
import numpy as np

from pathlib import Path

class HDF5Loader():
    """
    
    """
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.sample_rate = 100
        
        ### Conversion info for accelerometer
        self.accl_range = 8 # sensors default is (+/-8g)
        self.adc_range = 32767.0 # default ADC range is -32768 to 32767 (16 bit)

        with h5py.File(filepath, "r") as file:
            self.sensors = list(file.keys())

    def _ts_to_idx(self, ts: int) -> int:
        """Takes a time stamp and puts it as an index
            Args:
                ts (int): The current time stamp in milliseconds
            Return:
                idx (int): The index from the time stamp
        """        
        return int((ts / 1000) * self.sample_rate)

    def _calculate_start_stop(self, current_idx: int, margin_idx: int, max_idx: int) -> tuple[int, int]:
        """Takes the current timestamp and an amount of time around and gives a start and stop idx
            Args:
                current_idx (int) : The current idx
                margin_idx (int)  : The number of indices to move forward or back
                max_idx (int)     : The total number of samples
            Returns:
                start (int) : The start index of data to load 
                stop (int)  : The stop index of data to load
        """
        start = max(0, current_idx - margin_idx) 
        stop = min(max_idx, current_idx + margin_idx)
        return start, stop

    def get_chunks(self, current: int, margin: int) -> tuple[np.ndarray, np.ndarray]:
        """
            Args:
                current (int) : The current time in milliseconds
                margin (int)  : The amount around current to display in milliseconds
            Returns:
                chunks (tuple[np.ndarray, np.ndarray]) : The data loaded from the hdf5
        """
        current_idx = self._ts_to_idx(current)
        margin_idx = self._ts_to_idx(margin)

        with h5py.File(self.filepath, "r") as f:
            chunks = []
            for sensor in self.sensors:
                max_len = f[sensor].shape[0]
                start, stop = self._calculate_start_stop(current_idx, margin_idx, max_len)
                chunks.append(f[sensor][start:stop, :])
        return tuple(chunks)

    def get_chunks_accl(self, current: int, margin: int) -> tuple[np.ndarray, np.ndarray]:
        """
            Args:
                current (int) : The current time in milliseconds
                margin (int)  : The amount around current to display in milliseconds
            Returns:
                chunks (tuple[np.ndarray, np.ndarray]) : The magnitude of acceleration and the time stamp
        """
        current_idx = self._ts_to_idx(current)
        margin_idx = self._ts_to_idx(margin)

        with h5py.File(self.filepath, "r") as f:
            chunks = []
            for sensor in self.sensors:
                max_len = f[sensor].shape[0]
                start, stop = self._calculate_start_stop(current_idx, margin_idx, max_len)
                chunk = f[sensor][start:stop, :]
                accl = (self.accl_range/self.adc_range) * chunk[:, 0:3]
                mags = np.linalg.norm(accl, axis=1)
                mags_ts = np.column_stack((mags, chunk[:, 14]))
                chunks.append(mags_ts)
        return tuple(chunks)