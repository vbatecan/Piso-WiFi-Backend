import json
import sys
from datetime import datetime
from pathlib import Path
import pytest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app import app
from entities.Device import Device
from exceptions.DeviceExistsException import DeviceExistsException
from services.device_service import DeviceService

# Create a test client
client = TestClient(app)

# Test data
TEST_MAC_ADDRESS = "00:11:22:33:44:55"
TEST_DEVICE_PAYLOAD = {
    "mac_address": TEST_MAC_ADDRESS,
    "time_remaining": 3600,
    "last_connected": None,
    "is_active": True
}
TEST_DEVICE_MODEL = Device(**TEST_DEVICE_PAYLOAD)


@pytest.fixture(autouse=True)
def setup_teardown_method():
    # Setup: Ensure the device does not exist before certain tests
    # and mock the service
    # For most tests, we want a fresh state or controlled mocks.
    # Clean up any existing test device before each test that might create one.
    # This is a bit tricky as we don't want to delete if a test relies on its existence from a previous step (which is bad practice anyway)
    # A better approach for "conflict" is to mock the service layer.
    
    # Clear any actual device that might have been created by a previous test run if not properly mocked
    # This is a safeguard, primary reliance should be on mocks.
    with patch('controllers.device_controller.device_service', spec=DeviceService) as mock_service:
        # Reset global mock_service for safety, though patch should handle scope
        pass

    # Attempt to delete the test device from the actual DB to ensure a clean state for tests that might interact with it.
    # This is more of an integration test concern but good for robust test runs if mocks fail or are bypassed.
    # In a pure unit test, this would not be necessary if all service interactions are mocked.
    try:
        # Use the actual client to delete, as this is a cleanup step before tests
        # We assume the delete endpoint itself works for this cleanup.
        # If not, tests for delete will fail, which is fine.
        cleanup_response = client.delete(f"/device/{TEST_MAC_ADDRESS}")
        # Optionally log cleanup_response.status_code to see if cleanup was needed/successful
    except Exception:
        # Ignore if deletion fails (e.g., device not found, or DB issues)
        pass
    yield
    # Teardown: Clean up any device created during a test
    # Again, this is more for integration-style aspects or if mocks are bypassed.
    try:
        cleanup_response = client.delete(f"/device/{TEST_MAC_ADDRESS}")
    except Exception:
        pass


@patch('controllers.device_controller.device_service', spec=DeviceService)
def test_save_device_success(mock_device_service):
    mock_device_service.save.return_value = TEST_DEVICE_MODEL # Simulate successful save
    mock_device_service.exist.return_value = False # Ensure .exist() is also mocked if called by `save` or before

    response = client.post("/device/save", json=TEST_DEVICE_PAYLOAD)
    
    assert response.status_code == 200
    assert response.json()["mac_address"] == TEST_MAC_ADDRESS
    mock_device_service.save.assert_called_once()
    # Check that the correct Device object was passed to the service's save method
    called_arg = mock_device_service.save.call_args[0][0]
    assert isinstance(called_arg, Device)
    assert called_arg.mac_address == TEST_MAC_ADDRESS

@patch('controllers.device_controller.device_service', spec=DeviceService)
def test_save_device_conflict(mock_device_service):
    # Simulate device already exists by having save raise DeviceExistsException
    mock_device_service.save.side_effect = DeviceExistsException("Device already exists")

    response = client.post("/device/save", json=TEST_DEVICE_PAYLOAD)
    
    assert response.status_code == 409
    assert response.json()["error"] == "Device already exists"
    mock_device_service.save.assert_called_once()
    called_arg = mock_device_service.save.call_args[0][0]
    assert isinstance(called_arg, Device)
    assert called_arg.mac_address == TEST_MAC_ADDRESS

@patch('controllers.device_controller.device_service', spec=DeviceService)
def test_delete_device_success(mock_device_service):
    mock_device_service.delete.return_value = True # Simulate successful delete

    response = client.delete(f"/device/{TEST_MAC_ADDRESS}")

    assert response.status_code == 200
    assert response.json()["success"] == True
    mock_device_service.delete.assert_called_once_with(TEST_MAC_ADDRESS)

@patch('controllers.device_controller.device_service', spec=DeviceService)
def test_delete_device_not_found(mock_device_service):
    # Simulate device not found by having delete raise DeviceExistsException
    # (Note: The exception name might be confusing here, but it's what the controller uses for "not found" on delete)
    mock_device_service.delete.side_effect = DeviceExistsException("Device not found")

    response = client.delete(f"/device/{TEST_MAC_ADDRESS}")

    assert response.status_code == 404
    assert response.json()["error"] == "Device not found"
    assert response.json()["success"] == False
    mock_device_service.delete.assert_called_once_with(TEST_MAC_ADDRESS)

@patch('controllers.device_controller.device_service', spec=DeviceService)
def test_add_time_success(mock_device_service):
    mock_device_service.add_time.return_value = True # Simulate successful time addition
    time_to_add = 600 # 10 minutes

    response = client.patch(f"/device/add-time?mac_address={TEST_MAC_ADDRESS}&time={time_to_add}")

    assert response.status_code == 201
    assert response.json()["success"] == True
    mock_device_service.add_time.assert_called_once_with(TEST_MAC_ADDRESS, time_to_add)

@patch('controllers.device_controller.device_service', spec=DeviceService)
def test_add_time_device_not_found(mock_device_service):
    mock_device_service.add_time.side_effect = DeviceExistsException("Device not found to add time")
    time_to_add = 600

    response = client.patch(f"/device/add-time?mac_address={TEST_MAC_ADDRESS}&time={time_to_add}")

    assert response.status_code == 409 # As per controller logic for DeviceExistsException
    assert response.json()["error"] == "Device not found to add time"
    assert response.json()["success"] == False
    mock_device_service.add_time.assert_called_once_with(TEST_MAC_ADDRESS, time_to_add)

@patch('controllers.device_controller.device_service', spec=DeviceService)
def test_add_time_invalid_time_value(mock_device_service):
    # Simulate ValueError for invalid time (e.g. negative time)
    mock_device_service.add_time.side_effect = ValueError("Invalid time value")
    time_to_add = -100 # Invalid time

    response = client.patch(f"/device/add-time?mac_address={TEST_MAC_ADDRESS}&time={time_to_add}")

    assert response.status_code == 400 # Bad Request
    assert response.json()["error"] == "Invalid time value"
    assert response.json()["success"] == False
    mock_device_service.add_time.assert_called_once_with(TEST_MAC_ADDRESS, time_to_add)

@patch('controllers.device_controller.device_service', spec=DeviceService)
def test_reduce_time_success(mock_device_service):
    mock_device_service.reduce_time.return_value = True # Simulate successful time reduction
    time_to_reduce = 300 # 5 minutes

    response = client.patch(f"/device/reduce-time?mac_address={TEST_MAC_ADDRESS}&time={time_to_reduce}")

    assert response.status_code == 201
    assert response.json()["success"] == True
    mock_device_service.reduce_time.assert_called_once_with(TEST_MAC_ADDRESS, time_to_reduce)

@patch('controllers.device_controller.device_service', spec=DeviceService)
def test_reduce_time_device_not_found(mock_device_service):
    mock_device_service.reduce_time.side_effect = DeviceExistsException("Device not found to reduce time")
    time_to_reduce = 300

    response = client.patch(f"/device/reduce-time?mac_address={TEST_MAC_ADDRESS}&time={time_to_reduce}")

    assert response.status_code == 409 # As per controller for DeviceExistsException
    assert response.json()["error"] == "Device not found to reduce time"
    assert response.json()["success"] == False
    mock_device_service.reduce_time.assert_called_once_with(TEST_MAC_ADDRESS, time_to_reduce)

@patch('controllers.device_controller.device_service', spec=DeviceService)
def test_reduce_time_invalid_time_value(mock_device_service):
    # Simulate ValueError for invalid time (e.g. negative time)
    mock_device_service.reduce_time.side_effect = ValueError("Time to reduce cannot be negative")
    time_to_reduce = -100 # Invalid time

    response = client.patch(f"/device/reduce-time?mac_address={TEST_MAC_ADDRESS}&time={time_to_reduce}")

    assert response.status_code == 400 # Bad Request
    # The controller specifically returns "Please enter a valid time" for ValueError on reduce-time
    assert response.json()["error"] == "Please enter a valid time"
    assert response.json()["success"] == False
    mock_device_service.reduce_time.assert_called_once_with(TEST_MAC_ADDRESS, time_to_reduce)

@patch('controllers.device_controller.device_service', spec=DeviceService)
def test_get_device_success(mock_device_service):
    # Prepare a mock Device object to be returned by the service
    # Ensure last_connected is a string if it's part of the model and can be None/datetime
    # The TEST_DEVICE_MODEL already has last_connected=None, which should be handled by Pydantic to_dict/json methods
    mock_device_service.exist.return_value = True
    mock_device_service.get.return_value = TEST_DEVICE_MODEL

    response = client.get(f"/device/get?mac_address={TEST_MAC_ADDRESS}")

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["mac_address"] == TEST_MAC_ADDRESS
    assert response_data["time_remaining"] == TEST_DEVICE_MODEL.time_remaining
    # Assuming last_connected is serialized correctly (e.g., to None or ISO string)
    # If last_connected is None in the model, it should be None in JSON if not excluded.
    # If it's a datetime, it should be an ISO formatted string.
    # TEST_DEVICE_MODEL has last_connected=None
    assert response_data["last_connected"] == None 
    assert response_data["is_active"] == TEST_DEVICE_MODEL.is_active
    mock_device_service.exist.assert_called_once_with(TEST_MAC_ADDRESS)
    mock_device_service.get.assert_called_once_with(TEST_MAC_ADDRESS)

@patch('controllers.device_controller.device_service', spec=DeviceService)
def test_get_device_not_found(mock_device_service):
    mock_device_service.exist.return_value = False # Simulate device does not exist

    response = client.get(f"/device/get?mac_address={TEST_MAC_ADDRESS}")

    assert response.status_code == 404
    assert response.json()["error"] == "Device does not exist"
    assert response.json()["success"] == False
    mock_device_service.exist.assert_called_once_with(TEST_MAC_ADDRESS)
    mock_device_service.get.assert_not_called() # get should not be called if exist is false

# The global teardown_module is less ideal with per-test fixtures and mocks.
# If used, it would run once after all tests in the module.
# def teardown_module(module):
#     # This might try to delete a device that was part of a mocked test
#     # and never actually hit the DB, or was cleaned by a per-test fixture.
#     # client.delete(f"/device/{TEST_MAC_ADDRESS}")
#     pass

