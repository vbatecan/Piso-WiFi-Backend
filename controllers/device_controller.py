from fastapi import APIRouter, Response, status
from entities.Device import Device
from exceptions.DeviceExistsException import DeviceExistsException
from services.device_service import DeviceService

# Services
device_service = DeviceService()

router = APIRouter()

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
