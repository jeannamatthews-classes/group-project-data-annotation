import h5py
import numpy as np

from pathlib import Path
from typing import NoReturn

class HDF5Reader():
    """
    
    """
    def __init__(self, filepath: Path, idx_mode: bool = False):
        self.filepath = filepath
        self.sample_rate = 100
        self.idx_mode = idx_mode

        ### Conversion info for accelerometer
        self.accl_range = 8 # sensors default is (+/-8g)
        self.adc_range = 32767.0 # default ADC range is -32768 to 32767 (16 bit)

        with h5py.File(filepath, "r") as file:
            self.sensors = {k : 0 for k in list(file.keys())}

    def get_sensors(self) -> dict:
        return self.sensors

    def set_min(self, sensor_mac_addr: str, adjustment: int) -> NoReturn:
        """Allows user to set the min of the given sensor this enables them to set a new t0
            Args:
                sensor_mac_addr (str) : The string by which the sensor is identified
                adjustment (int) : The amount by which to change the min idx
            Returns:
                N/A
        """
        current_min = self.sensors[sensor_mac_addr] 
        new_min = max(0, current_min + adjustment)
        self.sensors[sensor_mac_addr] = new_min

    def _ts_to_idx(self, ts: int) -> int:
        """Takes a time stamp and puts it as an index
            Args:
                ts (int): The current time stamp in milliseconds
            Return:
                idx (int): The index from the time stamp
        """        
        return int((ts / 1000) * self.sample_rate)

    def _calculate_start_stop(self, current_idx: int, margin_idx: int, max_idx: int, edited_min: int) -> tuple[int, int]:
        """Takes the current timestamp and an amount of time around and gives a start and stop idx
            Args:
                current_idx (int) : The current idx
                margin_idx (int)  : The number of indices to move forward or back
                max_idx (int)     : The total number of samples
                set_min (int)     : The min set by the user for alignment 
            Returns:
                start (int) : The start index of data to load 
                stop (int)  : The stop index of data to load
        """
        if current_idx - margin_idx < 0:
            start = max(edited_min, current_idx - margin_idx + edited_min)
        else:
            start = max(0, current_idx - margin_idx + edited_min)
        stop = min(max_idx, current_idx + margin_idx + edited_min)
        return start, stop

    def get_chunks(self, current: int, margin: int, calc_accl=True) -> dict[str : np.ndarray]:
        """
            Args:
                current (int) : The current time in milliseconds
                margin (int)  : The amount around current to display in milliseconds
                calc_accl (bool)   : Calculate the acceleration magnitude
            Returns:
                chunks (dict[str, np.ndarray]) : The data loaded from the hdf5
        """
        if not self.idx_mode:
            current_idx = self._ts_to_idx(current)
            margin_idx = self._ts_to_idx(margin)
        else:
            current_idx = current
            margin_idx = margin

        with h5py.File(self.filepath, "r") as f:
            chunks = {}
            for sensor, edited_min in self.sensors.items():
                max_len = f[sensor].shape[0]
                start, stop = self._calculate_start_stop(current_idx, margin_idx, max_len, edited_min)
                chunk = f[sensor][start:stop, :]
                if calc_accl:
                    accl = (self.accl_range/self.adc_range) * chunk[:, 0:3]
                    mags = np.linalg.norm(accl, axis=1)
                    mags_ts = np.column_stack((mags, chunk[:, 14]))
                    chunks[sensor] = (mags_ts, start, stop)
                else: 
                    chunks[sensor] = (chunk, start, stop)
        return chunks