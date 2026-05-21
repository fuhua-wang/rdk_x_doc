---
sidebar_position: 7
---
# 8.7 Desktop Applications

This section primarily addresses issues encountered when using third-party applications on the desktop.

<!-- ```mdx-code-block
import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';
``` -->

### Q1: The downloaded Visual Studio Code application won't open?

<!-- <Tabs groupId="accessory">
<TabItem value="rdk_s600" label="rdk_s600"> -->

**A:**
* **Open via command line:** Visual Studio Code uses an Electron shell that has known issues with GPU (Graphics Processing Unit) hardware acceleration on certain systems. You can try disabling GPU acceleration by launching VS Code with the Electron `--disable-gpu` command-line flag (https://code.visualstudio.com/docs/supporting/faq#_vs-code-is-blank):

```bash
    code --disable-gpu
```
<!-- </TabItem>
</Tabs> -->

## Known Issues

1. The following issue may occur when switching languages
:::info Note
It is recommended to avoid using this feature for now. If you choose to use it, please refer to the steps below for a solution.
:::

Issue Description: After switching the system language in "Settings" and restarting, the desktop cannot be accessed even when the correct password is entered.

Steps: Open the Settings app, navigate to Region & Language, select the target language, and the restart button will appear (this restart only restarts the desktop session, not the device). Enter the password on the lock screen.

Solution: If you encounter the issue where the correct password is not accepted during the steps, power cycle the device or reboot it using the reboot command to complete the switch.