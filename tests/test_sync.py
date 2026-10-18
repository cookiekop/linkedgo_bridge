import ast
import asyncio
import importlib
from pathlib import Path
import random
import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import AsyncMock

from aiohttp import web
from aiohttp.test_utils import TestServer
import pytest

package = ModuleType('linkedgo_test')
package.__path__ = [str(Path(__file__).parents[1] / 'custom_components/linkedgo_bridge')]
sys.modules[package.__name__] = package
hub_module = importlib.import_module('linkedgo_test.hub')
api_module = importlib.import_module('linkedgo_test.xlink_api')
errors = importlib.import_module('linkedgo_test.errors')
DeviceEntity = importlib.import_module('linkedgo_test.const').DeviceEntity


def device():
    return DeviceEntity('model', 'ST830', 'climate', 0, 1, '00:00:00:00:00:01',
                        'Thermostat', '1', True, {}, {'7': 260, '6': 1, '116': 240})


class Cloud:
    def __init__(self):
        self.raw = dict(device().raw_data)
        self.sent = []
        self.online = True
        self.apply = True

    def encode_control(self, entity, service, value):
        return {service: value}

    def decode_state(self, product, raw):
        return {'temperature': raw['7'] / 10, 'fan_mode': raw['6'], 'current_temperature': raw['116'] / 10}

    async def async_home_device(self, home_id):
        entity = device()
        entity.online = self.online
        return [entity]

    async def async_batch_device_state(self, devices):
        return {'1': {'raw_data': dict(self.raw)}}

    async def async_set_datapoints(self, device_id, desired):
        self.sent.append(dict(desired))
        if not self.online:
            raise errors.DeviceOfflineError('Controller offline')
        if self.apply:
            self.raw.update(desired)


@pytest.fixture
def setup(monkeypatch):
    monkeypatch.setattr(hub_module, 'DEBOUNCE_SECONDS', .001)
    monkeypatch.setattr(hub_module, 'READBACK_SECONDS', .001)
    monkeypatch.setattr(hub_module, 'RETRY_SECONDS', .001)
    monkeypatch.setattr(hub_module, 'SYNC_TIMEOUT', .2)
    cloud = Cloud()
    hub = hub_module.Hub(cloud, lambda coroutine, name: asyncio.create_task(coroutine, name=name))
    return hub, cloud


async def complete(hub):
    await asyncio.wait_for(asyncio.gather(*list(hub._workers.values())), 1)


def test_rapid_edits_publish_immediately_and_send_only_final_values(setup):
    async def run():
        hub, cloud = setup
        entity = (await hub.async_refresh('home'))[0]
        values = random.Random(42).choices(range(100, 351, 5), k=50)
        for value in values:
            await hub.async_device_control(entity, '7', value)
            assert entity.properties['temperature'] == value / 10
        await hub.async_device_control(entity, '6', 3)
        assert cloud.sent == [] and hub.pending(entity)
        await complete(hub)
        assert cloud.sent == [{'7': values[-1], '6': 3}]
        assert entity.properties['temperature'] == values[-1] / 10
        assert entity.properties['fan_mode'] == 3
        assert entity.raw_data == cloud.raw
        assert not hub.pending(entity) and hub.sync_error(entity) is None
        cloud.raw['7'] = 270
        await hub.async_refresh('home')
        assert entity.properties['temperature'] == 27
    asyncio.run(run())


def test_poll_started_before_an_edit_cannot_overwrite_it(setup):
    async def run():
        hub, cloud = setup
        entity = (await hub.async_refresh('home'))[0]
        entered, release = asyncio.Event(), asyncio.Event()
        original = cloud.async_batch_device_state
        async def delayed(devices):
            old = await original(devices)
            entered.set()
            await release.wait()
            return old
        cloud.async_batch_device_state = delayed
        poll = asyncio.create_task(hub.async_refresh('home'))
        await entered.wait()
        await hub.async_device_control(entity, '7', 245)
        assert entity.properties['temperature'] == 24.5
        release.set()
        await poll
        assert entity.properties['temperature'] == 24.5
        cloud.async_batch_device_state = original
        await complete(hub)
        assert cloud.raw['7'] == 245 and not hub.pending(entity)
    asyncio.run(run())


def test_edit_during_command_supersedes_old_readback(setup):
    async def run():
        hub, cloud = setup
        entity = (await hub.async_refresh('home'))[0]
        entered, release = asyncio.Event(), asyncio.Event()
        original = cloud.async_set_datapoints
        async def delayed(device_id, desired):
            entered.set()
            await release.wait()
            await original(device_id, desired)
        cloud.async_set_datapoints = delayed
        await hub.async_device_control(entity, '7', 250)
        await entered.wait()
        await hub.async_device_control(entity, '7', 235)
        await hub.async_device_control(entity, '6', 2)
        assert entity.properties['temperature'] == 23.5
        release.set()
        await complete(hub)
        assert cloud.sent == [{'7': 250}, {'7': 235, '6': 2}]
        assert entity.properties['temperature'] == 23.5 and cloud.raw['7'] == 235
    asyncio.run(run())


def test_lagging_reports_keep_requested_value_until_confirmation(setup):
    async def run():
        hub, cloud = setup
        entity = (await hub.async_refresh('home'))[0]
        cloud.apply = False
        original = cloud.async_batch_device_state
        reads = 0
        async def lagging(devices):
            nonlocal reads
            reads += 1
            cloud.raw['116'] = 251
            if reads == 3:
                cloud.raw['7'] = 240
            return await original(devices)
        cloud.async_batch_device_state = lagging
        samples = []
        hub.on_update = lambda: samples.append((entity.properties['temperature'], hub.pending(entity)))
        await hub.async_device_control(entity, '7', 240)
        await complete(hub)
        assert reads == 3 and len(cloud.sent) == 1
        assert all(temp == 24 for temp, _ in samples)
        assert samples[-1] == (24, False)
        assert entity.properties['current_temperature'] == 25.1
    asyncio.run(run())


def test_offline_retry_preserves_latest_edit_and_recovers(setup):
    async def run():
        hub, cloud = setup
        entity = (await hub.async_refresh('home'))[0]
        failed = asyncio.Event()
        original = cloud.async_set_datapoints
        cloud.online = False
        async def track(device_id, desired):
            try:
                await original(device_id, desired)
            except errors.DeviceOfflineError:
                failed.set()
                raise
        cloud.async_set_datapoints = track
        await hub.async_device_control(entity, '7', 250)
        await failed.wait()
        assert hub.pending(entity) and entity.properties['temperature'] == 25
        await hub.async_device_control(entity, '7', 245)
        cloud.online = True
        await complete(hub)
        assert cloud.raw['7'] == 245 and entity.online
        assert hub.sync_error(entity) is None
        cloud.online = False
        await hub.async_refresh('home')
        assert not entity.online
        cloud.online = True
        await hub.async_refresh('home')
        assert entity.online
    asyncio.run(run())


def test_unconfirmed_change_expires_and_unload_cancels_pending_work(setup, monkeypatch):
    async def run():
        hub, cloud = setup
        entity = (await hub.async_refresh('home'))[0]
        cloud.apply = False
        monkeypatch.setattr(hub_module, 'SYNC_TIMEOUT', .01)
        await hub.async_device_control(entity, '7', 240)
        await complete(hub)
        assert not hub.pending(entity) and hub.sync_error(entity)
        assert entity.properties['temperature'] == 26
        assert len(cloud.sent) == 1
        monkeypatch.setattr(hub_module, 'DEBOUNCE_SECONDS', 10)
        await hub.async_device_control(entity, '7', 230)
        await hub.async_shutdown()
        assert not hub._workers and len(cloud.sent) == 1
    asyncio.run(run())


@pytest.mark.parametrize('status,body', [(400, {'error': {'code': 4001054, 'msg': 'device is offline'}}),
                                        (403, {'error': {'code': 4031021}}), (200, {})])
def test_http_errors_retain_status_and_body(status, body):
    async def run():
        async def response(request):
            return web.json_response(body, status=status)
        app = web.Application()
        app.router.add_post('/device', response)
        async with TestServer(app) as server:
            api = api_module.XlinkAPI()
            result = await api.send_request_async(str(server.make_url('/device')), {}, {'datapoint': []}, 'POST')
            assert result == (status, body)
    asyncio.run(run())


def test_device_offline_is_distinct_and_expired_auth_is_retried(monkeypatch):
    models = ModuleType('linkedgo_test.physical_model')
    models.XLINK_PHYSICAL_MODEL = {}
    monkeypatch.setitem(sys.modules, models.__name__, models)
    ptp_module = importlib.import_module('linkedgo_test.xlink_ptp')
    async def run():
        ptp = ptp_module.PTP()
        ptp.api = SimpleNamespace(async_send_multi_cmd=AsyncMock(return_value=(400, {'error': {'code': 4001064}})))
        with pytest.raises(errors.DeviceOfflineError):
            await ptp.async_set_datapoints(1, {'7': 245})
        ptp.api.async_send_multi_cmd = AsyncMock(side_effect=[(403, {}), (200, {})])
        ptp.async_user_auth = AsyncMock()
        await ptp.async_set_datapoints(1, {'7': 245})
        assert ptp.async_user_auth.await_count == 1
        assert ptp.api.async_send_multi_cmd.await_count == 2
        assert ptp.api.async_send_multi_cmd.call_args.args == (1, [{'index': 7, 'value': 245}])
    asyncio.run(run())


@pytest.mark.parametrize('model,index', [('ST830', 7), ('ST2000', 7), ('ST1800_HN', 1)])
def test_temperature_commands_encode_integer_datapoints(model, index):
    source = Path(package.__path__[0]) / 'physical_model' / f'{model}.py'
    method = next(node for node in ast.walk(ast.parse(source.read_text()))
                  if isinstance(node, ast.FunctionDef) and node.name == 'service_set_temperature')
    method.decorator_list = []
    namespace = {'Any': object}
    exec(compile(ast.Module(body=[method], type_ignores=[]), str(source), 'exec'), namespace)
    for temperature in (20.0, 23.5, 26.0):
        valid, points = namespace['service_set_temperature'](device(), temperature)
        assert valid and points == [{'index': index, 'value': int(temperature * 10)}]
        assert type(points[0]['value']) is int
