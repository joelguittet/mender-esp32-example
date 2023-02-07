# mender-esp32-example

[![CI Badge](https://github.com/joelguittet/mender-esp32-example/workflows/ci/badge.svg)](https://github.com/joelguittet/mender-esp32-example/actions)
[![Issues Badge](https://img.shields.io/github/issues/joelguittet/mender-esp32-example)](https://github.com/joelguittet/mender-esp32-example/issues)
[![License Badge](https://img.shields.io/github/license/joelguittet/mender-esp32-example)](https://github.com/joelguittet/mender-esp32-example/blob/master/LICENSE)

[Mender MCU client](https://github.com/joelguittet/mender-mcu-client) is an open source over-the-air (OTA) library updater for MCU devices. This demonstration project runs on ESP32 hardware.


## Getting started

This project is used with an [ESP32-WROOM-32D](https://www.espressif.com/sites/default/files/documentation/esp32-wroom-32d_esp32-wroom-32u_datasheet_en.pdf) module with 4MB flash. It should be compatible with other ESP32 modules with no modification.

The project is built using ESP-IDF v4.4 framework. There is no other dependencies. Important note: ESP-IDF v5.x is not compatible.

This project is developed under [VSCode](https://code.visualstudio.com) and using [ESP-IDF Extension](https://github.com/espressif/vscode-esp-idf-extension). If you need support to use the development environnement, you can refer to the "ESP-IDF Extension help" section below.

To start using Mender, we recommend that you begin with the Getting started section in [the Mender documentation](https://docs.mender.io/).

### Open the project

Clone the project and retrieve mender-mcu-client submodule using `git submodule update --init --recursive`.

Then open the project with VSCode.

### Configuration of the application

The example application should first be configured to set at least:
- `CONFIG_MENDER_SERVER_HOST` to set the server host. Default is valid for US `https://hosted.mender.io` and should be changed to `https://eu.hosted.mender.io` for EU/UK
- `MENDER_SERVER_TENANT_TOKEN` to set the Tenant Token of your account on the server host. This can be found as `Organization Token` in Account->My Organisation on the Mender.io portal.
- `CONFIG_EXAMPLE_WIFI_SSID` and `CONFIG_EXAMPLE_WIFI_PASSWORD` to connect the device to your own WiFi access point.

You may want to customize few interesting settings:
- `MENDER_SERVER_HOST` if using your own Mender server instance. Tenant Token is not required in this case.
- `MENDER_CLIENT_AUTHENTICATION_POLL_INTERVAL` is the interval to retry authentication on the mender server.
- `MENDER_CLIENT_INVENTORY_POLL_INTERVAL` is the interval to publish inventory data.
- `MENDER_CLIENT_UPDATE_POLL_INTERVAL` is the interval to check for new deployments.

Other settings are available in the menuconfig in sections "Example Configuration", "Example Connection Configuration" and "Mender client Configuration". You can also refer to the mender-mcu-client API.

### Execution of the application

After flashing the application on the ESP32 module and displaying logs, you should be able to see the following:

```
I (5660) main: Running project 'mender-esp32-example' version '0.1'
I (5670) mender: ../components/mender-mcu-client/mender-mcu-client/platform/board/esp32/src/mender-storage.c (48): Authentication keys are not available
I (5680) mender: ../components/mender-mcu-client/mender-mcu-client/src/mender-client.c (193): Generating authentication keys...
I (38320) mender: ../components/mender-mcu-client/mender-mcu-client/platform/board/esp32/src/mender-storage.c (103): OTA ID or artifact name not available
I (38320) main: Mender client initialized
I (40480) esp-x509-crt-bundle: Certificate validated
E (41910) mender: ../components/mender-mcu-client/mender-mcu-client/src/mender-api.c (626): [401] Unauthorized: unknown error
I (41910) main: Mender client authentication failed (1/3)
```

Which means you now have generated authentication keys on the device. Authentication keys are stored in NVS partition of the ESP32. You now have to accept your device on the mender interface. If you are not seeing anything on your Mender dashboard make sure you are in the correct domain (US/EU) and have the correct `MENDER_SERVER_HOST` set.

Once it is accepted on the mender interface the following will be displayed:

```
I (97707) esp-x509-crt-bundle: Certificate validated
I (99157) main: Mender client authenticated
I (99657) esp-x509-crt-bundle: Certificate validated
I (101597) esp-x509-crt-bundle: Certificate validated
I (102837) mender: ../components/mender-client/mender-client/src/mender-client.c (475): No deployment available
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
I (189677) esp-x509-crt-bundle: Certificate validated
I (190917) mender: ../components/mender-client/mender-client/src/mender-client.c (449): Downloading deployment artifact with id 'a95e6a3a-d0f5-4117-b575-118866f423d1', artifact name 'mender-esp32-example-v0.2' and uri 'https://s3.amazonaws.com/hosted-mender-artifacts/637c82337377ce997a5bda18/e1ec39a6-3b4e-47b9-9fe5-e3fcce05a319?X-Amz-Algorithm
I (191427) esp-x509-crt-bundle: Certificate validated
I (192857) main: Deployment status is 'downloading'
I (193357) esp-x509-crt-bundle: Certificate validated
I (195467) mender: ../components/mender-client/mender-client/platform/board/esp32/src/mender-ota.c (19): Start flashing OTA artifact 'mender-esp32-example.bin' with size 920096
I (195467) mender: ../components/mender-client/mender-client/platform/board/esp32/src/mender-ota.c (27): Next update partition is 'ota_1', subtype 17 at offset 0x210000 and with size 2031616
I (253047) esp_image: segment 0: paddr=00210020 vaddr=3f400020 size=2c33ch (181052) map
I (253107) esp_image: segment 1: paddr=0023c364 vaddr=3ffb0000 size=03bbch ( 15292) 
I (253117) esp_image: segment 2: paddr=0023ff28 vaddr=40080000 size=000f0h (   240) 
I (253117) esp_image: segment 3: paddr=00240020 vaddr=400d0020 size=9c69ch (640668) map
I (253327) esp_image: segment 4: paddr=002dc6c4 vaddr=400800f0 size=1431ch ( 82716) 
I (253357) esp_image: segment 5: paddr=002f09e8 vaddr=50000000 size=00010h (    16) 
I (253367) mender: ../components/mender-client/mender-client/src/mender-client.c (455): Download done, installing artifact
I (253877) esp-x509-crt-bundle: Certificate validated
I (255317) main: Deployment status is 'installing'
I (255317) mender: ../components/mender-client/mender-client/platform/board/esp32/src/mender-ota.c (90): Next update partition is 'ota_1', subtype 17 at offset 0x210000 and with size 2031616
I (255327) esp_image: segment 0: paddr=00210020 vaddr=3f400020 size=2c33ch (181052) map
I (255397) esp_image: segment 1: paddr=0023c364 vaddr=3ffb0000 size=03bbch ( 15292) 
I (255407) esp_image: segment 2: paddr=0023ff28 vaddr=40080000 size=000f0h (   240) 
I (255407) esp_image: segment 3: paddr=00240020 vaddr=400d0020 size=9c69ch (640668) map
I (255627) esp_image: segment 4: paddr=002dc6c4 vaddr=400800f0 size=1431ch ( 82716) 
I (255657) esp_image: segment 5: paddr=002f09e8 vaddr=50000000 size=00010h (    16) 
I (256227) esp-x509-crt-bundle: Certificate validated
I (257667) main: Deployment status is 'rebooting'
I (257667) main: Restarting system

...

I (5701) main: Running project 'mender-esp32-example' version '0.2'
I (5721) main: Mender client initialized
I (7751) esp-x509-crt-bundle: Certificate validated
I (9181) main: Mender client authenticated
I (9251) mender: ../components/mender-client/mender-client/platform/board/esp32/src/mender-ota.c (117): Application has been mark valid and rollback canceled
I (9691) esp-x509-crt-bundle: Certificate validated
I (11121) main: Deployment status is 'success'
I (11641) esp-x509-crt-bundle: Certificate validated
I (13571) esp-x509-crt-bundle: Certificate validated
I (14811) mender: ../components/mender-client/mender-client/src/mender-client.c (493): No deployment available
```

Congratulation! You have updated the device. Mender server displays the success of the deployment.

If the update is downloaded, verified, applied, and on reset you are still running the old version this might be because you have build with ESP-IDF 5.x SDK which as indicated above is not supported. You need to build with ESP-IDF 4.x SDK

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

Configure options of `.vscode/c_cpp_properties.json` if required (`compilerPath` particularly).

Now build the project with the `ESP-IDF: Build your project` command (Ctrl+E then B). Progress is displayed in the terminal.

Binary is generated in the build directory.

You may optionally want to display the size of the executable with `ESP-IDF: Size analysis of the binaries` command (Ctrl+E then S).

### Flashing

First select the wanted serial port corresponding to the target with the `ESP-IDF: Select port to use` command (Ctrl+E then P).

Then invoke the `ESP-IDF: Flash your project` command (Ctrl+E then F) to flash the target. Choose `UART` option.

### Monitoring

Logs are displayed using the `ESP-IDF: Monitor your device` command (Ctrl+E then M).
