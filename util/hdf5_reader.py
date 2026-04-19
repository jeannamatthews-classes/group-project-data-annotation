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

    def get_sync_timestamp(self, sensor_mac_addr: str) -> float:
        sync_idx = self.sensors[sensor_mac_addr]
        with h5py.File(self.filepath, "r") as f:
            return float(f[sensor_mac_addr][sync_idx, 14])

    def reset_mins(self):
        for sensor in self.sensors:
            self.sensors[sensor] = 0

    def set_min(self, sensor_mac_addr: str, new_min: int) -> NoReturn:
        """Allows user to adjust the min of the given sensor this enables them to set a new t0
            Args:
                sensor_mac_addr (str) : The string by which the sensor is identified
                new_min (int) : 
            Returns:
                N/A
        """
        self.sensors[sensor_mac_addr] = new_min

    def adjust_min(self, sensor_mac_addr: str, adjustment: int) -> NoReturn:
        """Allows user to adjust the min of the given sensor this enables them to set a new t0
            Args:
                sensor_mac_addr (str) : The string by which the sensor is identified
                adjustment (int) : The amount by which to change the min idx
            Returns:
                N/A
        """
        current_min = self.sensors[sensor_mac_addr] 
        new_min = max(0, current_min + adjustment)
        self.sensors[sensor_mac_addr] = new_min
    
    def get_chunks_by_time(self, center_ms: int, margin_ms: int, calc_accl=True) -> dict:
        chunks = {}
        with h5py.File(self.filepath, "r") as f:
            for sensor, sync_idx in self.sensors.items():
                timestamps = f[sensor][:, 14]
                sync_ts = timestamps[sync_idx]
                
                # Convert requested time range to sensor timestamps
                target_start_ts = sync_ts + (center_ms - margin_ms)
                target_stop_ts  = sync_ts + (center_ms + margin_ms)
                
                # Find indices closest to those timestamps
                start = max(0, np.searchsorted(timestamps, target_start_ts))
                stop  = min(len(timestamps), np.searchsorted(timestamps, target_stop_ts))
                
                chunk = f[sensor][start:stop, :]
                if calc_accl:
                    accl = (self.accl_range / self.adc_range) * chunk[:, 0:3]
                    mags = np.linalg.norm(accl, axis=1)
                    mags_ts = np.column_stack((mags, chunk[:, 14]))
                    chunks[sensor] = (mags_ts, start, stop)
                else:
                    chunks[sensor] = (chunk, start, stop)
        return chunks