---
sidebar_position: 2
---
```mdx-code-block
import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';
```

# RDK IMU Module (BMI088)

## Product Overview

The RDK IMU Module is the official IMU accessory from D-Robotics. It uses the Bosch **BMI088** solution, integrating a 3-axis gyroscope and a 3-axis accelerometer. It connects to RDK development boards via **I2C** or **SPI**. Raw sensor data can be read through the Linux IIO subsystem.

:::info Supported Platforms
This document applies to **RDK X5 / RDK X5 Module**. System image **3.4.x** is recommended (compatible with 3.5.x).
:::

## Installation

### Hardware Connection

<Tabs groupId="bmi088-interface">
<TabItem value="i2c" label="I2C Interface">

![rdk_x5_bmi088_hw_connect.png](http://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/03_Basic_Application/07_accessory_instructions/imu/rdk_x5_bmi088_hw_connect.png)

1. Connect the RDK IMU Module to the RDK X5 40-pin header according to the product manual.
2. Ensure the power and I2C pin connections are secure.

When using the I2C interface, run the following command to verify that the IMU is detected:

```shell
i2cdetect -y -r 5
```

![rdk_x5_bmi088_i2cdetect.png](http://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/03_Basic_Application/07_accessory_instructions/imu/rdk_x5_bmi088_i2cdetect.png)


</TabItem>
<TabItem value="spi" label="SPI Interface">

1. Connect the RDK IMU Module to the RDK X5 40-pin header according to the product manual.
2. Pay special attention to the carrier board header pins and ensure they are all inserted on the SPI side.

![rdk_x5_bmi088_hw_connect_spi.png](http://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/03_Basic_Application/07_accessory_instructions/imu/rdk_x5_bmi088_hw_connect_spi.png)

</TabItem>
</Tabs>

### Software Configuration

Run `sudo srpi-config` in a full-screen terminal and select the corresponding IMU option based on the interface type:

<Tabs groupId="bmi088-interface">
<TabItem value="i2c" label="I2C Interface">

1. Go to `3 Interface Options` → `I6 IMU`

![rdk_x5_bmi088_srpiconfig_1.png](http://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/03_Basic_Application/07_accessory_instructions/imu/rdk_x5_bmi088_srpiconfig_1.png)

![rdk_x5_bmi088_srpiconfig_2.png](http://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/03_Basic_Application/07_accessory_instructions/imu/rdk_x5_bmi088_srpiconfig_2.png)

2. Select `BMI088-I2C-Interface`

![rdk_x5_bmi088_srpiconfig_3.png](http://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/03_Basic_Application/07_accessory_instructions/imu/rdk_x5_bmi088_srpiconfig_3.png)

3. Select `Finish`, confirm, and choose `Yes` to reboot

![rdk_x5_bmi088_srpiconfig_4.png](http://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/03_Basic_Application/07_accessory_instructions/imu/rdk_x5_bmi088_srpiconfig_4.png)

![rdk_x5_bmi088_srpiconfig_5.png](http://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/03_Basic_Application/07_accessory_instructions/imu/rdk_x5_bmi088_srpiconfig_5.png)






</TabItem>
<TabItem value="spi" label="SPI Interface">

1. Go to `3 Interface Options` → `I6 IMU`

![rdk_x5_bmi088_srpiconfig_6.png](http://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/03_Basic_Application/07_accessory_instructions/imu/rdk_x5_bmi088_srpiconfig_6.png)

![rdk_x5_bmi088_srpiconfig_7.png](http://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/03_Basic_Application/07_accessory_instructions/imu/rdk_x5_bmi088_srpiconfig_7.png)

2. Select the **SPI** option for BMI088 (distinct from the I2C option; refer to the `srpi-config` menu)

![rdk_x5_bmi088_srpiconfig_8.png](http://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/03_Basic_Application/07_accessory_instructions/imu/rdk_x5_bmi088_srpiconfig_8.png)

3. Select `Finish`, confirm, and reboot

![rdk_x5_bmi088_srpiconfig_9.png](http://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/03_Basic_Application/07_accessory_instructions/imu/rdk_x5_bmi088_srpiconfig_9.png)

![rdk_x5_bmi088_srpiconfig_10.png](http://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/03_Basic_Application/07_accessory_instructions/imu/rdk_x5_bmi088_srpiconfig_10.png)

</TabItem>
</Tabs>

### Uninstallation

1. Go to `srpi-config` → `3 Interface Options` → `I6 IMU`
2. Select `UNSET` to remove the IMU driver and related configuration
3. Power off the board and remove the IMU module

## Operation

<Tabs groupId="bmi088-verify">
<TabItem value="i2c-verify" label="I2C Interface">

### 1. Check Devices

With the **I2C interface**, scan the I2C bus (bus number `5` is commonly used on RDK X5; adjust based on your wiring):

```shell
i2cdetect -y -r 5
```
![rdk_x5_bmi088_i2cdetect_2.png](http://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/03_Basic_Application/07_accessory_instructions/imu/rdk_x5_bmi088_i2cdetect_2.png)

If the scan shows one address as `UU` and another as `69`, **power off and reboot** the board before continuing.

Check input event nodes (the event number may vary depending on mount order):

```shell
ls /dev/input
```

Check IIO device nodes:

```shell
ls /sys/bus/iio/devices/
```

### 2. Basic Data Verification

Read IIO nodes directly for verification (the `iio:device` number should match the output of `ls /sys/bus/iio/devices/`):

```shell
cat /sys/bus/iio/devices/iio:device1/gyr_val
```

If you can read the correct `name` and values, the I2C path is working.

</TabItem>
<TabItem value="spi-verify" label="SPI Interface">

### 1. Check Devices

For this IMU, you can check whether registration succeeded directly:

```shell
dmesg | grep BS_LOG
```
![rdk_x5_bmi088_spi_dmesg.png](http://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/03_Basic_Application/07_accessory_instructions/imu/rdk_x5_bmi088_spi_dmesg.png)

### 2. Basic Data Verification

Read IIO nodes directly for verification (the `iio:device` number should match the output of `ls /sys/bus/iio/devices/`):

```shell
cat /sys/bus/iio/devices/iio:device1/gyr_val
```

If you can read the correct `name` and values, the SPI path is working. Example output:

![rdk_x5_bmi088_spi_cat_gyr_name.png](http://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/03_Basic_Application/07_accessory_instructions/imu/rdk_x5_bmi088_spi_cat_gyr_name.png)

![rdk_x5_bmi088_spi_cat_gyr_val.png](http://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/03_Basic_Application/07_accessory_instructions/imu/rdk_x5_bmi088_spi_cat_gyr_val.png)

![rdk_x5_bmi088_spi_cat_acc_val.png](http://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/03_Basic_Application/07_accessory_instructions/imu/rdk_x5_bmi088_spi_cat_acc_val.png)

Note: The actual IIO node numbers may differ depending on registered devices on the board. Always verify on your device.

</TabItem>
</Tabs>

## Troubleshooting

- **`i2cdetect` shows one `UU` and one `69`**: Power off and reboot the board, then scan again.
- **IIO device not found**: Confirm the correct interface type is selected in `srpi-config` and the board has been rebooted.
- **Device number differs from examples**: Use the actual registration results on your board.
