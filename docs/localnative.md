# LocalNative compatibility branch

`ha-compat` starts at upstream `v1.0.2` (`6c48969`). It normalizes firmware metadata
for Home Assistant 2026.10 and synchronizes thermostat settings in the background.
Device identities and existing configuration are preserved.

Panel edits update immediately. After one second without another edit, the latest
requested datapoints are sent together. Old polls cannot overwrite pending edits;
reported values are confirmed in the background. Normal device reports resume
after confirmation, including changes made on the physical controller.

Transient cloud failures are retried for up to approximately one minute after the
last edit. A failed synchronization restores the last reported state and exposes
`last_sync_error`; `pending_sync` distinguishes an unconfirmed edit from a completed
change. This avoids replaying a forgotten HVAC command much later. Pending changes
are canceled when the integration unloads or HA stops.

The integration polls LinkedGo's cloud; it is not a local push connection.
Availability is refreshed with each poll. API error codes are retained so expired
authentication can recover and offline controllers can be identified.

LocalNative pins this fork as a submodule and deploys only
`custom_components/linkedgo_bridge`. Upstream documentation is retained.

Run the isolated metadata regression check without installing Home Assistant:

```sh
uv run --no-project --with pytest --with aiohttp pytest tests
```

Review upstream changes before advancing the compatibility branch and the
LocalNative submodule pin. Do not install upstream HACS releases over this fork.
