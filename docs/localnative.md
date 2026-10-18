# LocalNative compatibility branch

`ha-compat` starts at upstream `v1.0.2` (`6c48969`). It normalizes non-null
firmware versions to strings for Home Assistant 2026.10 and later; HVAC behavior
and device identities are unchanged.

LocalNative pins this fork as a submodule and deploys only
`custom_components/linkedgo_bridge`. Upstream documentation is retained.

Run the isolated metadata regression check without installing Home Assistant:

```sh
uv run --no-project --with pytest pytest tests
```

Review upstream changes before advancing the compatibility branch and the
LocalNative submodule pin. Do not install upstream HACS releases over this fork.
