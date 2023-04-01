# mender-esp32-example

[![CI Badge](https://github.com/joelguittet/mender-esp32-example/workflows/ci/badge.svg)](https://github.com/joelguittet/mender-esp32-example/actions)
[![Issues Badge](https://img.shields.io/github/issues/joelguittet/mender-esp32-example)](https://github.com/joelguittet/mender-esp32-example/issues)
[![License Badge](https://img.shields.io/github/license/joelguittet/mender-esp32-example)](https://github.com/joelguittet/mender-esp32-example/blob/master/LICENSE)

[Mender MCU client](https://github.com/joelguittet/mender-mcu-client) is an open source over-the-air (OTA) library updater for MCU devices. This demonstration project runs on ESP32 hardware.


## Getting started

This project is used with an [ESP32-WROOM-32D](https://www.espressif.com/sites/default/files/documentation/esp32-wroom-32d_esp32-wroom-32u_datasheet_en.pdf) module with 4MB flash. It should be compatible with other ESP32 modules with no modification.

The project is built using ESP-IDF framework. There is no other dependencies. Important note: the project has been tested with ESP-IDF v4.4.x and v5.0.x successfully. There is no support for older releases.

This project is developed under [VSCode](https://code.visualstudio.com) and using [ESP-IDF Extension](https://github.com/espressif/vscode-esp-idf-extension). If you need support to use the development environnement, you can refer to the "ESP-IDF Extension help" section below.

To start using Mender, we recommend that you begin with the Getting started section in [the Mender documentation](https://docs.mender.io/).

### Open the project

Clone the project and retrieve mender-mcu-client submodule using `git submodule update --init --recursive`.

Then open the project with VSCode.

### Configuration of the application

The example application should first be configured to set at least:
- `MENDER_SERVER_TENANT_TOKEN` to set the Tenant Token of your account on "https://hosted.mender.io" server;
- `CONFIG_EXAMPLE_WIFI_SSID` and `CONFIG_EXAMPLE_WIFI_PASSWORD` to connect the device to your own WiFi access point.

You may want to customize few interesting settings:
- `MENDER_SERVER_HOST` if using your own Mender server instance. Tenant Token is not required in this case.
- `MENDER_CLIENT_AUTHENTICATION_POLL_INTERVAL` is the interval to retry authentication on the mender server.
- `MENDER_CLIENT_UPDATE_POLL_INTERVAL` is the interval to check for new deployments.
- `MENDER_CLIENT_INVENTORY_POLL_INTERVAL` is the interval to publish inventory data.

Other settings are available in the menuconfig in sections "Mender client Configuration", "Example Configuration" and "Example Connection Configuration". You can also refer to the mender-mcu-client API.

### Execution of the application

After flashing the application on the ESP32 module and displaying logs, you should be able to see the following:

```
I (5666) main: Running project 'mender-esp32-example' version '0.1'
I (5676) mender: ../components/mender-mcu-client/mender-mcu-client/platform/board/esp-idf/src/mender-storage.c (86): Authentication keys are not available
I (5686) mender: ../components/mender-mcu-client/mender-mcu-client/core/src/mender-client.c (330): Generating authentication keys...
I (5696) main: Mender client initialized
I (5706) main: Mender inventory initialized
I (14596) mender: ../components/mender-mcu-client/mender-mcu-client/platform/board/esp-idf/src/mender-storage.c (148): OTA ID or artifact name not available
I (16666) esp-x509-crt-bundle: Certificate validated
E (18196) mender: ../components/mender-mcu-client/mender-mcu-client/core/src/mender-api.c (701): [401] Unauthorized: unknown error
I (18196) main: Mender client authentication failed (1/3)
```

Which means you now have generated authentication keys on the device. Authentication keys are stored in NVS partition of the ESP32. You now have to accept your device on the mender interface. Once it is accepted on the mender interface the following will be displayed:

```
I (106776) esp-x509-crt-bundle: Certificate validated
I (108316) main: Mender client authenticated
I (108826) esp-x509-crt-bundle: Certificate validated
I (110876) esp-x509-crt-bundle: Certificate validated
I (112206) mender: ../components/mender-mcu-client/mender-mcu-client/core/src/mender-client.c (459): No deployment available
```

Congratulation! Your device is connected to the mender server. Device type is `mender-esp32-example` and the current software version is displayed.

### Create a new deployment

First retrieve [mender-artifact](https://docs.mender.io/downloads#mender-artifact) tool.

Change VERSION to `0.2` and rebuild the firmware. Then create a new artifact using the following command line:

```
./mender-artifact write rootfs-image --compression none --device-type mender-esp32-example --artifact-name mender-esp32-example-v0.2 --output-path build/mender-esp32-example-v0.2.mender --file build/mender-esp32-example.bin
```

Upload the artifact `mender-esp32-example-v0.2.mender` to the mender server and create a new deployment.

The device checks for the new deployment, downloads the artifact and installs it on the next ota partition. Then it reboots to apply the update:

```
I (288846) esp-x509-crt-bundle: Certificate validated
I (290886) esp-x509-crt-bundle: Certificate validated
I (292256) mender: ../components/mender-mcu-client/mender-mcu-client/core/src/mender-client.c (471): Downloading deployment artifact with id '28a65724-ad35-439a-b8c2-7a6154258cc9', artifact name 'mender-esp32-example-v0.2' and uri 'https://s3.amazonaws.com/hosted-mender-artifacts/637c82337377ce997a5bda18/e1bfc2c2-764e-44d2-aeb4-f64b1f207429?X-Amz-Algorit
I (292736) esp-x509-crt-bundle: Certificate validated
I (294276) main: Deployment status is 'downloading'
I (294786) esp-x509-crt-bundle: Certificate validated
I (296756) mender: ../components/mender-mcu-client/mender-mcu-client/platform/board/esp-idf/src/mender-ota.c (38): Start flashing OTA artifact 'mender-esp32-example.bin' with size 925904
I (296756) mender: ../components/mender-mcu-client/mender-mcu-client/platform/board/esp-idf/src/mender-ota.c (50): Next update partition is 'ota_1', subtype 17 at offset 0x210000 and with size 2031616
I (356666) esp_image: segment 0: paddr=00210020 vaddr=3f400020 size=2f32ch (193324) map
I (356726) esp_image: segment 1: paddr=0023f354 vaddr=3ffb0000 size=00cc4h (  3268) 
I (356736) esp_image: segment 2: paddr=00240020 vaddr=400d0020 size=9a7a4h (632740) map
I (356946) esp_image: segment 3: paddr=002da7cc vaddr=3ffb0cc4 size=02b94h ( 11156) 
I (356946) esp_image: segment 4: paddr=002dd368 vaddr=40080000 size=14d28h ( 85288) 
I (356976) esp_image: segment 5: paddr=002f2098 vaddr=50000000 size=00010h (    16) 
I (356986) mender: ../components/mender-mcu-client/mender-mcu-client/core/src/mender-client.c (480): Download done, installing artifact
I (357456) esp-x509-crt-bundle: Certificate validated
I (358986) main: Deployment status is 'installing'
I (358996) mender: ../components/mender-mcu-client/mender-mcu-client/platform/board/esp-idf/src/mender-ota.c (121): Next update partition is 'ota_1', subtype 17 at offset 0x210000 and with size 2031616
I (359006) esp_image: segment 0: paddr=00210020 vaddr=3f400020 size=2f32ch (193324) map
I (359076) esp_image: segment 1: paddr=0023f354 vaddr=3ffb0000 size=00cc4h (  3268) 
I (359086) esp_image: segment 2: paddr=00240020 vaddr=400d0020 size=9a7a4h (632740) map
I (359296) esp_image: segment 3: paddr=002da7cc vaddr=3ffb0cc4 size=02b94h ( 11156) 
I (359296) esp_image: segment 4: paddr=002dd368 vaddr=40080000 size=14d28h ( 85288) 
I (359326) esp_image: segment 5: paddr=002f2098 vaddr=50000000 size=00010h (    16) 
I (359906) esp-x509-crt-bundle: Certificate validated
I (361246) main: Deployment status is 'rebooting'
I (361256) main: Restarting system

...

I (5724) main: Running project 'mender-esp32-example' version '0.2'
I (5744) main: Mender client initialized
I (5744) main: Mender inventory initialized
I (7804) esp-x509-crt-bundle: Certificate validated
I (9184) main: Mender client authenticated
I (9254) mender: ../components/mender-mcu-client/mender-mcu-client/platform/board/esp-idf/src/mender-ota.c (149): Application has been mark valid and rollback canceled
I (9694) esp-x509-crt-bundle: Certificate validated
I (11024) main: Deployment status is 'success'
I (11534) esp-x509-crt-bundle: Certificate validated
I (13374) esp-x509-crt-bundle: Certificate validated
I (14504) mender: ../components/mender-mcu-client/mender-mcu-client/core/src/mender-client.c (459): No deployment available
```

Congratulation! You have updated the device. Mender server displays the success of the deployment.

### Failure or wanted rollback

In case of failure to connect and authenticate to the server the current example application performs a rollback to the previous release.
You can customize the behavior of the example application to add your own checks and perform the rollback in case the tests fail.

### Using an other ESP32 module

The main requirement is the size of the flash that should be 4MB or more. You can increase the ota partitions in `partitions.csv` file if your module has more memory.


## ESP-IDF Extension help

### Building

Using VSCode, first open the directory of the project.

Then go to Command Palette (Ctrl+Shift+P) and execute the `ESP-IDF: Set Espressif device target` command to select select an Espressif target. Choose `esp32`, then select `Custom board`.

Next execute the `ESP-IDF: SDK Configuration editor` command (Ctrl+E then G) to generate sdkconfig and optionally modify project settings. After all changes are made, click save and close this window.

Now build the project with the `ESP-IDF: Build your project` command (Ctrl+E then B). Progress is displayed in the terminal.

Binary is generated in the build directory.

You may optionally want to display the size of the executable with `ESP-IDF: Size analysis of the binaries` command (Ctrl+E then S).

### Flashing

First select the wanted serial port corresponding to the target with the `ESP-IDF: Select port to use` command (Ctrl+E then P).

Then invoke the `ESP-IDF: Flash your project` command (Ctrl+E then F) to flash the target. Choose `UART` option.

### Monitoring

Logs are displayed using the `ESP-IDF: Monitor your device` command (Ctrl+E then M).
