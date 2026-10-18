# Author: 彩色不倒翁 2577811496@qq.com
# Date: 2023-02-14 10:50:39
# LastEditors: 彩色不倒翁 2577811496@qq.com
# LastEditTime: 2023-02-14 11:53:39
# FilePath: \xlink_data_import\xlink_api.py
# Description: 云智易接口请求API封装类

import logging
import aiohttp
import urllib.request
import json
import datetime
import threading
from enum import StrEnum

_LOGGER = logging.getLogger(__name__)


class XlinkFields(StrEnum):
    """Xlink IOT platform response fiedlds."""

    ACCESS_TOKEN = "access_token"
    REFRESH_TOKEN = "refresh_token"
    USER_ID = "user_id"
    EXPIRE_IN = "expire_in"
    AUTHORIZE = "authorize"

    HOME_ID = "id"
    HOME_NAME = "name"

    LAST_LOGIN = "last_login"
    MCU_VERSION = "mcu_version"
    MAC = "mac"
    PRODUCT_ID = "product_id"
    DEVICE_NAME = "name"
    DEVICE_ID = "id"
    ONLINE = "is_online"

    LIST = "list"

    # 4031021: Access Token Expired
    # 4031022: Access-Token Refresh
    # 4001010: Refresh Token Expired
    CODE = "code"


class XlinkAPI(object):
    """Xlink http request api."""

    REQUEST_METHOD_GET = "GET"
    REQUEST_METHOD_POST = "POST"

    _instance_lock = threading.Lock()

    # RestUri preffix
    base_url = "https://api2.xlink.cn"

    # company identifer
    corp_id = "100fa6b2eddf2400"

    # refresh token in advance seconds
    refresh_token_timeout = 600

    # aceess token
    access_token = None

    # refresh token
    refresh_token = None

    # user identifer
    user_id = None

    # expire time
    expire_time = None

    # authorize code
    authorize_code = None

    def __init__(self):
        """Initiate XlinkAPI class."""

    # single instance
    def __new__(cls, *args, **kwargs):
        if not hasattr(XlinkAPI, "_instance"):
            with XlinkAPI._instance_lock:
                if not hasattr(XlinkAPI, "_instance"):
                    XlinkAPI._instance = object.__new__(cls)
        return XlinkAPI._instance

    def send_request_sync(self, rest_url: str, headers, request_body, method):
        """Send https request in synchronize method.

        :param rest_url: request url.
        :param headers: request headers.
        :param request_body: request body.
        :param method:  request method.
        :return: (HttpStatusCode/None, None/BodyString/BodyJson)
        :rtype: Set
        """
        if request_body:
            request = urllib.request.Request(
                url=rest_url,
                headers=headers,
                data=json.dumps(request_body).encode("utf-8"),
                method=method,
            )
        else:
            request = urllib.request.Request(
                url=rest_url, headers=headers, method=method
            )

        try:
            response = urllib.request.urlopen(request)
        except Exception as e:
            error_info = str(e)
            _LOGGER.error(error_info)
            return None, None
        else:
            if response:
                code = response.getcode()
                str_result = response.read().decode("utf-8")
                if code == 200:
                    rsp_json = json.loads(str_result)
                    return code, rsp_json
                _LOGGER.error(
                    f"Req url: {rest_url}\nRsp code: {code}\nRsp body: {str_result}"
                )
                return code, str_result
            return None, None

    async def send_request_async(self, rest_url, headers, request_body, method):
        """Preserve API errors so callers can distinguish rejection from stale state."""
        timeout = aiohttp.ClientTimeout(total=15)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                kwargs = {} if method.upper() == "GET" else {"json": request_body}
                async with session.request(method, rest_url, headers=headers, **kwargs) as response:
                    try:
                        body = await response.json(content_type=None)
                    except (ValueError, UnicodeDecodeError):
                        _LOGGER.error("LinkedGo returned a non-JSON response (HTTP %s)", response.status)
                        return response.status, None
                    return response.status, body
        except (aiohttp.ClientError, TimeoutError) as error:
            _LOGGER.error("LinkedGo request failed: %s", type(error).__name__)
            return None, None

    def user_login(self, usename, password):
        """User login.

        :param use_name: user name or account, email or phone number.
        :param password: password.
        :return: (respond code, respond body, in format of json).
        :rtype: Set
        """
        suffix = "/v2/user_auth"
        rest_url = self.base_url + suffix

        headers = {"Content-Type": "application/json"}

        request_body = {
            "corp_id": self.corp_id,
            "phone": usename,
            "password": password,
            "resource": "web",
        }

        code, rsp_json = self.send_request_sync(
            rest_url, headers, request_body, self.REQUEST_METHOD_POST
        )

        if code == 200 and isinstance(rsp_json, dict):
            if XlinkFields.ACCESS_TOKEN in rsp_json:
                self.access_token = rsp_json[XlinkFields.ACCESS_TOKEN]
                self.refresh_token = rsp_json[XlinkFields.REFRESH_TOKEN]
                self.user_id = rsp_json[XlinkFields.USER_ID]
                self.authorize_code = rsp_json[XlinkFields.AUTHORIZE]
                expire_timeout = rsp_json[XlinkFields.EXPIRE_IN]
                self.expire_time = datetime.datetime.now() + datetime.timedelta(
                    seconds=expire_timeout
                )
        return code, rsp_json

    async def async_user_login(self, use_name, password):
        """User login.

        :param use_name: user name or account, email or phone number.
        :param password: password.
        :return: (respond code, respond body, in format of json).
        :rtype: Set
        """
        suffix = "/v2/user_auth"
        rest_url = self.base_url + suffix

        headers = {"Content-Type": "application/json"}

        request_body = {
            "corp_id": self.corp_id,
            "phone": use_name,
            "password": password,
            "resource": "web",
        }

        code, rsp_json = await self.send_request_async(
            rest_url, headers, request_body, self.REQUEST_METHOD_POST
        )

        if code == 200 and isinstance(rsp_json, dict):
            if XlinkFields.ACCESS_TOKEN in rsp_json:
                self.access_token = rsp_json[XlinkFields.ACCESS_TOKEN]
                self.refresh_token = rsp_json[XlinkFields.REFRESH_TOKEN]
                self.user_id = rsp_json[XlinkFields.USER_ID]
                self.authorize_code = rsp_json[XlinkFields.AUTHORIZE]
                expire_timeout = rsp_json[XlinkFields.EXPIRE_IN]
                self.expire_time = datetime.datetime.now() + datetime.timedelta(
                    seconds=expire_timeout
                )

        return code, rsp_json

    async def async_refresh_token(self):
        """Refresh token.

        :param use_name: user name or account, email or phone number.
        :param password: password.
        :return: (respond code, respond body, in format of json).
        :rtype: Set
        """
        suffix = "/v2/user/token/refresh"
        rest_url = self.base_url + suffix

        headers = {
            "Access-Token": self.access_token,
            "Content-Type": "application/json",
        }

        request_body = {"refresh_token": self.refresh_token}

        code, rsp_json = await self.send_request_async(
            rest_url, headers, request_body, self.REQUEST_METHOD_POST
        )

        if code == 200 and isinstance(rsp_json, dict):
            if XlinkFields.ACCESS_TOKEN in rsp_json:
                self.access_token = rsp_json[XlinkFields.ACCESS_TOKEN]
                self.refresh_token = rsp_json[XlinkFields.REFRESH_TOKEN]
                expire_timeout = rsp_json[XlinkFields.EXPIRE_IN]
                self.expire_time = datetime.datetime.now() + datetime.timedelta(
                    seconds=expire_timeout
                )

        return code, rsp_json

    async def async_user_home(self, user_id):
        """User home list.

        :param user_id: user identifer.
        :return: (respond code, respond body, in format of json).
        :rtype: Set
        """
        suffix = f"/v2/homes?user_id={user_id}&field=room,zone&version=0".format(
            user_id=user_id
        )
        rest_url = self.base_url + suffix

        headers = {
            "Access-Token": self.access_token,
            "Content-Type": "application/json",
        }

        request_body = None

        code, rsp_json = await self.send_request_async(
            rest_url, headers, request_body, self.REQUEST_METHOD_GET
        )

        return code, rsp_json

    # list of devices belong to certain home
    # home_id: home identifer
    # Return: (respond code, respond body, in format of json)
    async def async_home_devices(self, home_id):
        """Query vitual device state in batches.

        :param product_id: produce identifer.
        :param device_list: list of device.
        :param value: setting value.
        :return: (respond code, respond body, in format of json).
        :rtype: Set
        """
        if isinstance(home_id, int):
            home_id = str(home_id)
        suffix = f"/v2/home/{home_id}/devices".format(home_id=home_id)
        rest_url = self.base_url + suffix

        headers = {
            "Access-Token": self.access_token,
            "Content-Type": "application/json",
        }

        request_body = None

        code, rsp_json = await self.send_request_async(
            rest_url, headers, request_body, self.REQUEST_METHOD_GET
        )

        return code, rsp_json

    async def async_batch_query_vdevice(self, product_id, device_list):
        """Query vitual device state in batches.

        :param product_id: produce identifer.
        :param device_list: list of device.
        :param value: setting value.
        :return: (respond code, respond body, in format of json).
        :rtype: Set
        """
        suffix = f"/v2/product/{product_id}/v_devices".format(product_id=product_id)
        rest_url = self.base_url + suffix

        headers = {
            "Access-Token": self.access_token,
            "Content-Type": "application/json",
        }

        request_body = device_list

        code, rsp_json = await self.send_request_async(
            rest_url, headers, request_body, self.REQUEST_METHOD_POST
        )
        return code, rsp_json

    async def async_send_cmd(self, device_id, index, value):
        """Device control.

        :param device_id: device identifer.
        :param index: filed identifer of physical model.
        :param value: setting value.
        :return: (respond code, respond body, in format of json).
        :rtype: Set
        """
        suffix = f"/v2/diagnosis/device/set/{device_id}".format(device_id=device_id)
        rest_url = self.base_url + suffix

        headers = {
            "Access-Token": self.access_token,
            "Content-Type": "application/json",
        }

        request_body = {"datapoint": [{"index": index, "value": value}]}

        code, rsp_json = await self.send_request_async(
            rest_url, headers, request_body, self.REQUEST_METHOD_POST
        )
        return code, rsp_json

    async def async_send_multi_cmd(self, device_id, dps):
        """Device control.

        :param device_id: device identifer.
        :param dps: data points.
        :return: (respond code, respond body, in format of json).
        :rtype: Set
        """
        suffix = f"/v2/diagnosis/device/set/{device_id}".format(device_id=device_id)
        rest_url = self.base_url + suffix

        headers = {
            "Access-Token": self.access_token,
            "Content-Type": "application/json",
        }

        request_body = {"datapoint": dps}

        code, rsp_json = await self.send_request_async(
            rest_url, headers, request_body, self.REQUEST_METHOD_POST
        )
        return code, rsp_json

    def authorization_validate(self, timedelta=0):
        """Validate authorization.

        :param timedelta: time delta seconds.
        :return: Ture-valid, False-invalid.
        :rtype: bool
        """
        if self.access_token and self.expire_time is not None:
            current_time = datetime.datetime.now()
            if self.expire_time > (
                current_time + datetime.timedelta(seconds=timedelta)
            ):
                return True
        return False
