---
sidebar_position: 1
---

# rdk-backup

The **rdk-backup** command backs up the current system into an image file.

## Syntax

```
sudo rdk-backup [dir]
```

## Parameters

`dir` is the working directory used to build and mount the image package. The default is `/mnt`.

The packaging directory is ignored while the image is being produced.

## Common usage

Network access is required first; **rdk-backup** downloads and installs tools it needs during execution.

```
sudo rdk-backup
```

When finished, the backup image appears under the packaging directory as `rdk-<timestamp>.img`.
