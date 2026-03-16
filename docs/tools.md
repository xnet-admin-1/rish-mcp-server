# Available Tools

## shizuku_shell

Execute arbitrary shell commands with Shizuku privileges.

```json
{
  "command": "id",
  "timeout": 30
}
```

## shizuku_pm

Package manager operations.

```json
{
  "args": "list packages -f",
  "timeout": 30
}
```

## shizuku_am

Activity manager operations.

```json
{
  "args": "start -n com.android.settings/.Settings",
  "timeout": 30
}
```

## shizuku_dumpsys

System service information.

```json
{
  "service": "battery"
}
```

## shizuku_settings

System settings manipulation.

```json
{
  "namespace": "global",
  "command": "get",
  "key": "wifi_on"
}
```

## shizuku_status

Check server configuration and availability.

```json
{}
```
