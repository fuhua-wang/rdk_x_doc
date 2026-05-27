---
sidebar_position: 1
---
```mdx-code-block
import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';
import DocScope from '@site/src/components/DocScope';
```

# Waveshare Audio Driver HAT REV2

## Product Introduction

The Audio Driver HAT REV2 is an audio adapter board manufactured by Waveshare Electronics. It uses the ES7210+ES8156 dual Codec solution and supports features such as circular 4-microphone recording, dual-channel audio playback, and audio signal loopback. The appearance of the adapter board is shown below:

![image-audio-driver-hat](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/03_Basic_Application/02_audio/image/image-audio-driver-hat.jpg)

For more details about the audio daughter board, please refer to [Audio Driver HAT](https://www.waveshare.net/shop/Audio-Driver-HAT.htm).

## Installation Guide

- ### Hardware Setup

<DocScope versions=">= 3.0.0" products="RDK X3">

1. Connect the adapter board to the 40-pin header of the RDK X3 as shown in the figure below.
![image-audio-driver-hat-setup](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/03_Basic_Application/02_audio/image/image-audio-driver-hat-setup.jpg)

</DocScope>

<DocScope versions=">= 3.0.0" products="RDK X3 Module">

1. Connect the adapter board to the 40-pin header of the RDK X3 as shown in the figure below.
![image-x3md-v2](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/03_Basic_Application/02_audio/image/image-x3md-v2.png)

</DocScope>

2. Use the command `cat /sys/class/socinfo/som_name` to check the development board type, and set the DIP switch status of the audio daughter board based on the returned value.
   - If the returned value is 5 or 6, set all 3 DIP switches to the `ON` position.
   - If the returned value is 8, set all 3 DIP switches to the `OFF` position.

- ### Software Configuration

1. Configure the audio board using `srpi-config`
Navigate to `3 Interface Options` -> `I5 Audio`
Select `Audio Driver HAT V2`:
![image-audio-driver-hat-config00](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/03_Basic_Application/02_audio/image/image-audio-driver-hat-config00.png)

2. Run the command `sync && reboot` to restart the development board. If the following device nodes appear under `ls /dev/snd`, the adapter board has been successfully installed.
    ```shell
    root@ubuntu:/userdata# ls /dev/snd
    by-path  controlC0  pcmC0D0c  pcmC0D1p  timer
    ```

- ### Uninstallation Guide
1. Configure the audio board using `srpi-config`
Navigate to `3 Interface Options` -> `I5 Audio`
Select `UNSET` to uninstall the audio driver and related configurations.

2. Disconnect the carrier board.

## Operation

### 1. Check the Sound Card Device

First, verify whether the sound card has been correctly recognized and registered by the system.

- View the list of registered sound cards:

    ```shell
    cat /proc/asound/cards
    ```
    Example output:
    ```
     root@ubuntu:~# cat /proc/asound/cards
     0 [hobotsnd5      ]: hobotsnd5 - hobotsnd5
                          hobotsnd5

    ```
    If an entry like "hobotsnd5" appears, the sound card has been recognized.

- View the functional devices under the sound card:
    ```shell
    cat /proc/asound/devices
    ```
    Example output:
    ```
    root@ubuntu:~# cat /proc/asound/devices
        2: [ 0]   : control
        3: [ 0- 0]: digital audio playback
        4: [ 0- 1]: digital audio capture
        33:        : timer
    ```

### 2. Recording Operation

<DocScope versions=">= 3.0.0" products="RDK X3">

- **2-Channel Microphone Recording**
  Use tinycap to record 2-channel audio:

  ```shell
  tinycap ./2chn_test.wav -D 0 -d 1 -c 2 -b 16 -r 48000 -p 512 -n 4 -t 5
  ```

- **4-Channel Microphone Recording**

  ```shell
  tinycap ./4chn_test.wav -D 0 -d 1 -c 4 -b 16 -r 48000 -p 512 -n 4 -t 5
  ```

### 3. Playback Operation

- **Dual-Channel Audio Playback (4-channel playback not supported)**
  Use tinyplay to play the recorded audio file:

  ```shell
  tinyplay ./2chn_test.wav -D 0 -d 0
  ```

### 4. Audio Loopback Test

The audio loopback function can be used to capture the signal from the playback channel for subsequent analysis.

- **8-Channel Microphone Recording (including loopback)**
  The loopback signal of this audio board is mapped to recording channels 7 and 8. Use the 8-channel recording command:

  ```shell
  tinycap ./8chn_test.wav -D 0 -d 1 -c 8 -b 16 -r 48000 -p 512 -n 4 -t 5
  ```

- **Simultaneously start dual-channel audio playback**

  ```shell
  tinyplay ./2chn_test.wav -D 0 -d 0
  ```

- **Analyze the loopback signal**
  After recording, use audio analysis software such as Audacity to open `8chn_test.wav` and check the waveforms or spectrums of channels 7 and 8 to verify if the loopback function is working properly.

</DocScope>

<DocScope versions=">= 3.0.0" products="RDK X3 Module">

- **2-Channel Microphone Recording**
  Use tinycap to record 2-channel audio:

  ```shell
  tinycap ./2chn_test.wav -D 0 -d 0 -c 2 -b 16 -r 48000 -p 512 -n 4 -t 5
  ```

- **4-Channel Microphone Recording**

  ```shell
  tinycap ./4chn_test.wav -D 0 -d 0 -c 4 -b 16 -r 48000 -p 512 -n 4 -t 5
  ```

### 3. Playback Operation

- **Dual-Channel Audio Playback (4-channel playback not supported)**
  Use tinyplay to play the recorded audio file:

  ```shell
  tinyplay ./2chn_test.wav -D 0 -d 1
  ```

### 4. Audio Loopback Test

The audio loopback function can be used to capture the signal from the playback channel for subsequent analysis.

- **8-Channel Microphone Recording (including loopback)**
  The loopback signal of this audio board is mapped to recording channels 7 and 8. Use the 8-channel recording command:

  ```shell
  tinycap ./8chn_test.wav -D 0 -d 0 -c 8 -b 16 -r 48000 -p 512 -n 4 -t 5
  ```

- **Simultaneously start dual-channel audio playback**

  ```shell
  tinyplay ./2chn_test.wav -D 0 -d 1
  ```

- **Analyze the loopback signal**
  After recording, use audio analysis software such as Audacity to open `8chn_test.wav` and check the waveforms or spectrums of channels 7 and 8 to verify if the loopback function is working properly.
</DocScope>

## Troubleshooting Common Issues

- If the sound card is not detected, check whether the hardware connections and DIP switch settings are correct.
- If there is no sound during recording or playback, verify that the audio file format and number of channels match the command parameters.
- If there is no signal on the loopback channel, ensure that the 8-channel recording command has been used correctly.

For other issues, please refer to [Audio Common Issues](../../../08_FAQ/04_multimedia.md#audio-faqs) for more assistance.