"""Synchronize device reports without overwriting newer panel edits."""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Coroutine
import logging
from time import monotonic
from typing import Any, TYPE_CHECKING

from .const import DeviceEntity
from .errors import APIREQUESTError, DeviceOfflineError

if TYPE_CHECKING:
    from .xlink_ptp import PTP

_LOGGER = logging.getLogger(__name__)
DEBOUNCE_SECONDS = 1.0
READBACK_SECONDS = 2.0
RETRY_SECONDS = 5.0
SYNC_TIMEOUT = 60.0


class Hub:
    manufacturer = "Linkedgo"

    def __init__(
        self, ptp: PTP, create_task: Callable[[Coroutine[Any, Any, None], str], asyncio.Task[None]]
    ) -> None:
        self._create_task = create_task
        self.ptp = ptp
        self.devices: list[DeviceEntity] = []
        self.on_update: Callable[[], None] = lambda: None
        self._io_lock = asyncio.Lock()
        self._pending: dict[str, dict[str, Any]] = {}
        self._revision: dict[str, int] = {}
        self._requested_at: dict[str, float] = {}
        self._errors: dict[str, str] = {}
        self._workers: dict[str, asyncio.Task[None]] = {}
        self._stopping = False

    def pending(self, entity: DeviceEntity) -> bool:
        return bool(self._pending.get(str(entity.device_id)))

    def sync_error(self, entity: DeviceEntity) -> str | None:
        return self._errors.get(str(entity.device_id))

    def _publish_properties(self, entity: DeviceEntity) -> None:
        raw = dict(entity.raw_data or {})
        raw.update(self._pending.get(str(entity.device_id), {}))
        entity.properties.update(self.ptp.decode_state(entity.product_id, raw))

    async def async_refresh(self, home_id: str) -> list[DeviceEntity]:
        revisions = dict(self._revision)
        async with self._io_lock:
            discovered = await self.ptp.async_home_device(home_id)
            if not self.devices:
                self.devices = discovered
            metadata = {str(entity.device_id): entity for entity in discovered}
            devices = {entity.device_id: entity.product_id for entity in discovered}
            reports = await self.ptp.async_batch_device_state(devices) if devices else {}
        for entity in self.devices:
            key = str(entity.device_id)
            if revisions.get(key, 0) != self._revision.get(key, 0):
                continue
            current = metadata.get(key)
            entity.online = bool(current and current.online and key in reports)
            if report := reports.get(key):
                entity.raw_data = report["raw_data"]
                self._publish_properties(entity)
        return self.devices

    async def async_device_control(self, entity: DeviceEntity, service: str, value: Any) -> None:
        if self._stopping:
            raise APIREQUESTError("LinkedGo is unloading; please try again after reload")
        key = str(entity.device_id)
        desired = self.ptp.encode_control(entity, service, value)
        self._pending.setdefault(key, {}).update(desired)
        self._revision[key] = self._revision.get(key, 0) + 1
        self._requested_at[key] = monotonic()
        self._errors.pop(key, None)
        self._publish_properties(entity)
        self.on_update()
        if key not in self._workers:
            self._workers[key] = self._create_task(
                self._sync_device(entity), f"LinkedGo settings {key}"
            )

    async def _readback(self, entity: DeviceEntity, revision: int, desired: dict[str, Any]) -> bool:
        key = str(entity.device_id)
        async with self._io_lock:
            reports = await self.ptp.async_batch_device_state({entity.device_id: entity.product_id})
        if revision != self._revision[key]:
            return False
        report = reports.get(key)
        if not report:
            return False
        raw: dict[str, Any] = report["raw_data"]
        entity.raw_data = raw
        confirmed = all(raw.get(field) == value for field, value in desired.items())
        if confirmed:
            self._pending.pop(key, None)
            self._errors.pop(key, None)
            self._revision[key] += 1
            entity.online = True
        self._publish_properties(entity)
        self.on_update()
        return confirmed

    async def _sync_device(self, entity: DeviceEntity) -> None:
        key = str(entity.device_id)
        last_error = "LinkedGo did not confirm the requested settings within 60 seconds"
        try:
            while self.pending(entity):
                revision = self._revision[key]
                await asyncio.sleep(DEBOUNCE_SECONDS)
                if revision != self._revision[key]:
                    continue
                remaining = SYNC_TIMEOUT - (monotonic() - self._requested_at[key])
                if remaining <= 0:
                    self._fail(entity, last_error)
                    return
                desired = dict(self._pending[key])
                try:
                    async with asyncio.timeout(remaining):
                        async with self._io_lock:
                            # The user may edit again while a poll holds the connection.
                            if revision != self._revision[key]:
                                continue
                            await self.ptp.async_set_datapoints(entity.device_id, desired)
                        while revision == self._revision[key]:
                            if await self._readback(entity, revision, desired):
                                break
                            await asyncio.sleep(READBACK_SECONDS)
                except (APIREQUESTError, TimeoutError) as error:
                    if revision != self._revision[key]:
                        continue
                    if isinstance(error, DeviceOfflineError):
                        entity.online = False
                    if isinstance(error, APIREQUESTError):
                        last_error = str(error)
                    await asyncio.sleep(RETRY_SECONDS)
        except asyncio.CancelledError:
            raise
        except Exception:
            _LOGGER.exception("Unexpected LinkedGo synchronization failure for %s", entity.device_name)
            self._fail(entity, "LinkedGo synchronization failed; please try again")
        finally:
            self._workers.pop(key, None)

    def _fail(self, entity: DeviceEntity, message: str) -> None:
        key = str(entity.device_id)
        self._pending.pop(key, None)
        self._errors[key] = message
        self._revision[key] += 1
        self._publish_properties(entity)
        _LOGGER.warning("%s: %s", entity.device_name, message)
        self.on_update()

    async def async_shutdown(self) -> None:
        self._stopping = True
        tasks = list(self._workers.values())
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        self._workers.clear()
        self._pending.clear()
