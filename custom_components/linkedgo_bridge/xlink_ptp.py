"""API Placeholder.

You should create your api seperately and have it hosted on PYPI.  This is included here for the sole purpose
of making this example code executable.
"""

import logging
from collections.abc import Callable
from typing import Any
from enum import StrEnum

from .xlink_api import XlinkAPI, XlinkFields
from .physical_model import XLINK_PHYSICAL_MODEL
from .const import DeviceEntity
from .errors import APIREQUESTError, DeviceOfflineError

_LOGGER = logging.getLogger(__name__)


class PTPFields(StrEnum):
    HOME_ID = "home_id"
    HOME_NAME = "home_name"


class PTP:
    """Class for transformation from Xlink protocol to HomeAssistant protocol."""

    def __init__(self) -> None:
        """Initiate PTP class."""
        self.api = XlinkAPI()
        self.username = None
        self.password = None

    def user_auth(self, username, password) -> str:
        """User login.

        :return: user_id, login success; Exception, login falied.
        :rtype: str
        """
        if username:
            self.username = username
        if password:
            self.password = password
        code, rsp_json = self.api.user_login(username, password)
        if code and code == 200:
            if rsp_json and XlinkFields.ACCESS_TOKEN in rsp_json:
                return rsp_json[XlinkFields.USER_ID]
            raise APIDATAEMPTYError("Reponse data empty!")
        _LOGGER.error("LinkedGo authorization failed")
        raise APIAuthError("Invalid credentials!")

    async def async_user_auth(self, username, password) -> str:
        """User login.

        :return: user_id, login success; Exception, login falied.
        :rtype: str
        """
        if username:
            self.username = username
        if password:
            self.password = password
        code, rsp_json = await self.api.async_user_login(username, password)
        if code and code == 200:
            if rsp_json and XlinkFields.ACCESS_TOKEN in rsp_json:
                return rsp_json[XlinkFields.USER_ID]
            raise APIDATAEMPTYError("Reponse data empty!")
        _LOGGER.error("LinkedGo authorization failed")
        raise APIAuthError("Invalid credentials!")

    async def async_user_home(self) -> list[dict[str, Any]]:
        """Query user home list.

        :return: [{"home_id": "id", "name": "name"},].
        :rtype: List
        """
        code, rsp_json = await self.api.async_user_home(self.api.user_id)
        if code and code == 200:
            if rsp_json:
                homes = []
                home_list = rsp_json[XlinkFields.LIST]
                for home_info in home_list:
                    home = {}
                    home[PTPFields.HOME_ID] = home_info[XlinkFields.HOME_ID]
                    home[PTPFields.HOME_NAME] = home_info[XlinkFields.HOME_NAME]
                    homes.append(home)
                return homes
            raise APIDATAEMPTYError("Reponse data empty!")
        _LOGGER.error(f"Query user home failed, userid: {self.api.user_id}.")
        raise APIREQUESTError("Request failed!")

    async def async_home_device(self, home_id) -> list[DeviceEntity]:
        """Query home device list.

        :return: [{"device_id": "id", "device_type": "type", "device_name": "name"},].
        :rtype: List
        """
        code, rsp_json = await self.api.async_home_devices(home_id)
        if code == 403:
            await self.async_user_auth(self.username, self.password)
            code, rsp_json = await self.api.async_home_devices(home_id)
        if code and code == 200:
            if rsp_json:
                devices: list[DeviceEntity] = []
                device_list = rsp_json[XlinkFields.LIST]
                for device_info in device_list:
                    product_id = device_info[XlinkFields.PRODUCT_ID]
                    if product_id in XLINK_PHYSICAL_MODEL:
                        model_class = XLINK_PHYSICAL_MODEL[product_id]
                        produdct_model = getattr(model_class, "model")
                        ha_type = getattr(model_class, "ha_type")
                        ha_supported_features = getattr(
                            model_class, "ha_supported_features"
                        )
                        attributes: dict[str, Callable[[dict], tuple[bool, Any]]] = getattr(model_class, "attributes", {})
                        properties = {}
                        for field, func in attributes.items():
                            if callable(func):
                                ret, value = func({})
                                if ret:
                                    properties[field] = value
                        devices.append(
                            DeviceEntity(
                                product_id=device_info[XlinkFields.PRODUCT_ID],
                                product_model=produdct_model,
                                ha_type=ha_type,
                                ha_supported_features=ha_supported_features,
                                device_id=device_info[XlinkFields.DEVICE_ID],
                                device_mac=device_info[XlinkFields.MAC],
                                device_name=device_info[XlinkFields.DEVICE_NAME],
                                sw_version=device_info[XlinkFields.MCU_VERSION],
                                online=device_info[XlinkFields.ONLINE],
                                properties=properties,
                                raw_data=None,
                            )
                        )
                return devices
            raise APIDATAEMPTYError("Reponse data empty!")
        _LOGGER.error(f"Query home devices failed, homeid: {home_id}.")
        raise APIREQUESTError("Request failed!")

    def encode_control(self, entity: DeviceEntity, service: str, value: Any) -> dict[str, Any]:
        model = XLINK_PHYSICAL_MODEL.get(entity.product_id)
        encoder: Callable[[DeviceEntity, Any], tuple[bool, list[dict[str, Any]] | None]] | None = getattr(model, "services", {}).get(service)
        if not callable(encoder):
            raise APIREQUESTError(f"Unsupported LinkedGo action: {service}")
        valid, datapoints = encoder(entity, value)
        if not valid or not datapoints:
            raise APIREQUESTError(f"Unsupported LinkedGo value for {service}: {value}")
        return {str(point["index"]): point["value"] for point in datapoints}

    @staticmethod
    def decode_state(product_id: str, raw: dict[str, Any]) -> dict[str, Any]:
        model = XLINK_PHYSICAL_MODEL[product_id]
        properties = {}
        for field, decoder in model.attributes.items():
            valid, value = decoder(raw)
            if valid:
                properties[field] = value
        return properties

    async def async_set_datapoints(self, device_id: str | int, values: dict[str, Any]) -> None:
        datapoints = [{"index": int(index), "value": value} for index, value in values.items()]
        code, response = await self.api.async_send_multi_cmd(device_id, datapoints)
        if code == 403:
            await self.async_user_auth(self.username, self.password)
            code, response = await self.api.async_send_multi_cmd(device_id, datapoints)
        if code != 200:
            error = response.get("error", {}) if isinstance(response, dict) else {}
            error_code = error.get("code") if isinstance(error, dict) else None
            if error_code in (4001054, 4001064):
                raise DeviceOfflineError("LinkedGo cannot reach this controller; the setting was not confirmed")
            raise APIREQUESTError(f"LinkedGo rejected the setting (HTTP {code}, error {error_code})")

    async def async_batch_device_state(self, devices: dict) -> dict:
        """Batch request device states.

        :return: [{"device_id": {"properties":{}, "raw_data": {}}"},]
        :rtype: dict
        """

        pid_to_devices = {}
        # Group devices by pid
        for dev, pid in devices.items():
            device_list = pid_to_devices.get(pid, [])
            device_list.append(dev)
            pid_to_devices[pid] = device_list

        devices_state = {}
        # For each pid group, query the state and decode
        for pid, devs in pid_to_devices.items():
            code, rsp_json = await self.api.async_batch_query_vdevice(pid, devs)
            if code == 403:
                await self.async_user_auth(self.username, self.password)
                code, rsp_json = await self.api.async_batch_query_vdevice(pid, devs)
            if code == 200 and rsp_json:
                states = rsp_json.get(XlinkFields.LIST, [])
                for state in states:
                    device_id = state.get("device_id")
                    if device_id is not None:
                        devices_state[str(device_id)] = {
                            "properties": self.decode_state(pid, state),
                            "raw_data": state,
                        }
            else:
                raise APIREQUESTError(f"LinkedGo state query failed (HTTP {code})")

        # Check wether access token is going to be timeout. If it is, refresh token.
        is_valid = self.api.authorization_validate(timedelta=6900)
        if not is_valid:
            code, rsp_json = await self.api.async_refresh_token()
            if code == 200:
                _LOGGER.info("Refresh token and refresh token successfully")
            elif code == 403:
                _LOGGER.warning(
                    f"Refresh token request was forbidden, error message: {rsp_json}"
                )
                await self.async_user_auth(self.username, self.password)
            else:
                _LOGGER.error(f"Refresh token failed, error message: {rsp_json}")

        return devices_state

    def authorization_validate(self, timedelta=0):
        """Check whether access token is going to be timeout in 'timedelta' seconds.

        :param device_id: device identifer.
        :return: False - timeout or invalid, True - valid.
        :rtype: bool
        """
        return self.api.authorization_validate(timedelta)


class APIAuthError(Exception):
    """Exception class for auth error."""


class APIDATAEMPTYError(Exception):
    """Exception class for data empty error."""
