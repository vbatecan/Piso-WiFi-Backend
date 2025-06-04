from datetime import datetime
import logging
from fastapi import APIRouter, Response, status
from entities.Device import Device
from exceptions.DeviceExistsException import DeviceExistsException
from services.device_service import DeviceService

logger = logging.getLogger(__name__)
# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="device_controller.log",
    level=logging.DEBUG,
)

# Services
device_service = DeviceService()

router = APIRouter()


@router.post("/connected")
async def connected(mac_address: str, response: Response):
    try:
        if device_service.exist(mac_address):
            response.status_code = status.HTTP_200_OK
            device_service.connected(mac_address)
            device = device_service.get(mac_address)
            return {"success": True, "device": device}
        else:
            response.status_code = status.HTTP_201_CREATED
            device_service.save(
                Device(
                    mac_address=mac_address,
                    time_remaining=0,
                    last_connected=datetime.now(),
                    is_active=True,
                )
            )
            device = device_service.get(mac_address)
            return {"success": True, "device": device}

    except DeviceExistsException as e:
        logger.error("Device already exists: %s", e)
        response.status_code = status.HTTP_409_CONFLICT
        return {"error": str(e), "success": False}


@router.post("/disconnected")
async def disconnected(mac_address: str, response: Response):
    try:
        if device_service.exist(mac_address):
            if device_service.disconnected(mac_address):
                device = device_service.get(mac_address)
                response.status_code = status.HTTP_200_OK
                return {"success": True, "device": device}
            else:
                response.status_code = status.HTTP_409_CONFLICT
                return {"error": "Device is not connected", "success": False}
        else:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {"error": "Device does not exist", "success": False}
    except DeviceExistsException as e:
        logger.error("Device does not exist: %s", e)
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": str(e), "success": False}


@router.post("/save")
async def save_device(device: Device, response: Response):
    try:
        if device_service.save(device):
            return device
        response.status_code = status.HTTP_409_CONFLICT
        return {"error": "Device already exists", "success": False}
    except DeviceExistsException as e:
        response.status_code = status.HTTP_409_CONFLICT
        return {"error": str(e), "success": False}


@router.delete("/{mac_address}")
async def delete_device(mac_address: str, response: Response):
    try:
        response.status_code = status.HTTP_200_OK
        return {"success": device_service.delete(mac_address)}
    except DeviceExistsException as e:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": str(e), "success": False}


@router.patch("/add-time")
async def add_time(mac_address: str, time: int, response: Response):
    try:
        response.status_code = 201
        return {"success": device_service.add_time(mac_address, time)}
    except DeviceExistsException as e:
        response.status_code = status.HTTP_409_CONFLICT
        return {"error": str(e), "success": False}
    except ValueError as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": str(e), "success": False}


@router.patch("/reduce-time")
async def reduce_time(mac_address: str, time: int, response: Response):
    try:
        response.status_code = 201
        return {"success": device_service.reduce_time(mac_address, time)}
    except DeviceExistsException as e:
        response.status_code = status.HTTP_409_CONFLICT
        return {"error": str(e), "success": False}
    except ValueError as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "Please enter a valid time", "success": False}


@router.get("/get")
async def get_device(mac_address: str, response: Response):
    try:
        if device_service.exist(mac_address):
            return device_service.get(mac_address)

        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Device does not exist", "success": False}
    except DeviceExistsException as e:
        return {"error": str(e), "success": False}
