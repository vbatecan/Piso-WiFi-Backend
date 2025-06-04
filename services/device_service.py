from datetime import datetime
import sqlite3
import logging

from entities.Device import Device
from exceptions.DeviceExistsException import DeviceExistsException

logging.basicConfig(
    filename="debug.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s:%(name)s:%(message)s",
    datefmt="%Y-%m-%d %H:%M",
)
log = logging.getLogger("DeviceService")


class DeviceService:
    def __init__(self):
        self.con = sqlite3.connect("database.db")
        self.cur = self.con.cursor()

    def save(self, device: Device):
        try:
            if device.mac_address and self.exist(device.mac_address):
                log.debug("Device %s already exists", device.mac_address)
                raise DeviceExistsException(
                    f"Device {device.mac_address} already exists"
                )

            self.cur.execute(
                "INSERT INTO devices (mac_address, time_remaining, last_connected, is_active) VALUES (?, ?, ?, ?)",
                (
                    device.mac_address,
                    device.time_remaining,
                    device.last_connected,
                    device.is_active,
                ),
            )
            self.con.commit()
            log.debug("Device %s was added.", device.mac_address)
            return self.cur.rowcount > 0
        except sqlite3.Error as e:
            log.error("Database error: %s", e)
            self.con.rollback()
            exit(1)  # There shouldn't be an error.
        return False

    def update(self, device: Device):
        if self.exist(device.mac_address):
            self.cur.execute(
                "UPDATE devices SET time_remaining = ?, last_connected = ?, is_active = ? WHERE mac_address = ?",
                (
                    device.time_remaining,
                    device.last_connected,
                    device.is_active,
                    device.mac_address,
                ),
            )
            self.con.commit()
            return self.cur.rowcount > 0
        raise DeviceExistsException(f"Device {device.mac_address} does not exist")

    def delete(self, mac_address):
        if self.exist(mac_address):
            self.cur.execute(
                "DELETE FROM devices WHERE mac_address = ?", (mac_address,)
            )
            self.con.commit()
            return self.cur.rowcount > 0
        raise DeviceExistsException(f"Device {mac_address} does not exist")

    def get(self, mac_address):
        self.cur.execute("SELECT * FROM devices WHERE mac_address = ?", (mac_address,))
        result = self.cur.fetchone()
        if result is None:
            raise DeviceExistsException(f"Device {mac_address} does not exist")
        return Device(
            mac_address=result[1],
            time_remaining=result[2],
            last_connected=result[3],
            is_active=result[4],
        )

    def add_time(self, mac_address, time):
        try:
            time = int(time)
            device: Device = self.get(mac_address)
            device.time_remaining += time
            self.update(device)
            return True
        except ValueError as e:
            raise ValueError("Time must be an integer") from e
        except DeviceExistsException as e:
            raise DeviceExistsException(str(e)) from e

    def is_expired(self, mac_address):
        try:
            device = self.get(mac_address)
            return device.time_remaining <= 0
        except DeviceExistsException as e:
            raise DeviceExistsException(str(e)) from e

    def reduce_time(self, mac_address, time):
        try:
            time = int(time)
            device: Device = self.get(mac_address)
            # Prevents negative time which can possibly cause bugs.
            if device.time_remaining - time <= 0:
                device.time_remaining = 0
            else:
                device.time_remaining -= time
            self.update(device)
            return True
        except ValueError as e:
            raise ValueError("Time must be an integer") from e
        except DeviceExistsException as e:
            raise DeviceExistsException(str(e)) from e

    def connected(self, mac_address):
        try:
            device = self.get(mac_address)
            device.last_connected = datetime.now()
            device.is_active = True
            self.update(device)
            log.debug("Device %s was connected.", mac_address)
            return True
        except DeviceExistsException as e:
            raise DeviceExistsException(str(e)) from e

    def disconnected(self, mac_address):
        try:
            device = self.get(mac_address)
            device.is_active = False
            self.update(device)
            log.debug("Device %s was disconnected.", mac_address)
            return True
        except DeviceExistsException as e:
            raise DeviceExistsException(str(e)) from e
        except sqlite3.Error as e:
            log.error("Database error: %s", e)
            self.con.rollback()
            exit(1)  # There shouldn't be an error.
        return False

    def exist(self, mac_address):
        self.cur.execute(
            "SELECT COUNT(*) FROM devices WHERE mac_address = ?", (mac_address,)
        )
        result = self.cur.fetchone()
        return result is not None and result[0] > 0
