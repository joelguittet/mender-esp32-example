# mender-esp32-example

[![CI Badge](https://github.com/joelguittet/mender-esp32-example/workflows/ci/badge.svg)](https://github.com/joelguittet/mender-esp32-example/actions)
[![Issues Badge](https://img.shields.io/github/issues/joelguittet/mender-esp32-example)](https://github.com/joelguittet/mender-esp32-example/issues)
[![License Badge](https://img.shields.io/github/license/joelguittet/mender-esp32-example)](https://github.com/joelguittet/mender-esp32-example/blob/master/LICENSE)

[Mender MCU client](https://github.com/joelguittet/mender-mcu-client) is an open source over-the-air (OTA) library updater for MCU devices. This demonstration project runs on ESP32 hardware.


## Getting started

This project is used with an [ESP32-WROOM-32D](https://www.espressif.com/sites/default/files/documentation/esp32-wroom-32d_esp32-wroom-32u_datasheet_en.pdf) module with 4MB flash. It should be compatible with other ESP32 modules with no modification.

The project is built using ESP-IDF framework. There is no other dependencies. Important note: the project has been tested with ESP-IDF v4.4.x and v5.0.x successfully. There is no support for older releases.

This project is developed under [VSCode](https://code.visualstudio.com) and using [ESP-IDF Extension](https://github.com/espressif/vscode-esp-idf-extension). If you need support to use the development environment, you can refer to the "ESP-IDF Extension help" section below.

To start using Mender, we recommend that you begin with the Getting started section in [the Mender documentation](https://docs.mender.io/).

### Open the project

Clone the project and retrieve submodules using `git submodule update --init --recursive`.

Then open the project with VSCode.

### Configuration of the application

The example application should first be configured to set at least:
- `CONFIG_MENDER_SERVER_TENANT_TOKEN` to set the Tenant Token of your account on "https://hosted.mender.io" server;
- `CONFIG_EXAMPLE_WIFI_SSID` and `CONFIG_EXAMPLE_WIFI_PASSWORD` to connect the device to your own WiFi access point.

You may want to customize few interesting settings:
- `CONFIG_MENDER_SERVER_HOST` if using your own Mender server instance. Tenant Token is not required in this case.
- `CONFIG_MENDER_CLIENT_AUTHENTICATION_POLL_INTERVAL` is the interval to retry authentication on the mender server.
- `CONFIG_MENDER_CLIENT_UPDATE_POLL_INTERVAL` is the interval to check for new deployments.
- `CONFIG_MENDER_CLIENT_INVENTORY_REFRESH_INTERVAL` is the interval to publish inventory data.
- `CONFIG_MENDER_CLIENT_CONFIGURE_REFRESH_INTERVAL` is the interval to refresh device configuration.

Other settings are available in the Kconfig. You can also refer to the mender-mcu-client API and configuration keys.

Particularly, it is possible to activate the Device Troubleshoot add-on that will permit to display the logs of the ESP32 directly on the Mender interface as shown on the following screenshot.

![Troubleshoot console](https://raw.githubusercontent.com/joelguittet/mender-esp32-example/master/.github/docs/troubleshoot.png)

Note this also constraints to download [esp_websocket_client](https://components.espressif.com/components/espressif/esp_websocket_client) in vscode, which is compatible with ESP-IDF v5.0 and later only.

### Execution of the application

After flashing the application on the ESP32 module and displaying logs, you should be able to see the following:

```
I (640) main: MAC address of the device '7c:9e:bd:ed:bc:1c'
I (650) main: Running project 'mender-esp32-example' version '0.1'
I (660) main: Mender client initialized
I (660) main: Mender inventory add-on registered
I (680) mender: ./components/mender-mcu-client/mender-mcu-client/platform/storage/esp-idf/nvs/src/mender-storage.c (163): Deployment data not available
I (680) main: Mender client connect network
I (690) example_connect: Start example_connect.

... (wifi connecting to the network)

I (5560) example_connect: Got IPv4 event: Interface "example_netif_sta" address: 192.168.2.140
I (5640) example_connect: Got IPv6 event: Interface "example_netif_sta" address: fe80:0000:0000:0000:7e9e:bdff:feed:bc1c, type: 
ESP_IP6_ADDR_IS_LINK_LOCAL
I (5640) example_common: Connected to example_netif_sta
I (5650) example_common: - IPv4 address: 192.168.2.140,
I (5650) example_common: - IPv6 address: fe80:0000:0000:0000:7e9e:bdff:feed:bc1c, type: ESP_IP6_ADDR_IS_LINK_LOCAL
I (7740) esp-x509-crt-bundle: Certificate validated
I (8870) HTTP_CLIENT: Body received in fetch header state, 0x3ffc9b11, 86
E (8870) mender: ./components/mender-mcu-client/mender-mcu-client/core/src/mender-api.c (900): [401] Unauthorized: dev auth: unauthorized
I (8880) main: Mender client authentication failed
I (8880) main: Mender client released network
```

Which means you now have generated authentication keys on the device. Authentication keys are stored in NVS partition of the ESP32. You now have to accept your device on the mender interface. Once it is accepted on the mender interface the following will be displayed:

```
I (60670) main: Mender client connect network
I (60670) example_connect: Start example_connect.

... (wifi connecting to the network)

I (65640) example_common: Connected to example_netif_sta
I (65650) example_common: - IPv4 address: 192.168.2.140,
I (65650) example_common: - IPv6 address: fe80:0000:0000:0000:7e9e:bdff:feed:bc1c, type: ESP_IP6_ADDR_IS_LINK_LOCAL
I (68150) esp-x509-crt-bundle: Certificate validated
I (69290) HTTP_CLIENT: Body received in fetch header state, 0x3ffc6070, 156
I (69290) main: Mender client authenticated
I (69290) mender: ./components/mender-mcu-client/mender-mcu-client/core/src/mender-client.c (884): Checking for deployment...
I (69740) esp-x509-crt-bundle: Certificate validated
I (70720) mender: ./components/mender-mcu-client/mender-mcu-client/core/src/mender-client.c (892): No deployment available
I (70720) main: Mender client released network
```

Congratulation! Your device is connected to the mender server. Device type is `mender-esp32-example` and the current software version is displayed.

### Create a new deployment

First retrieve [mender-artifact](https://docs.mender.io/downloads#mender-artifact) tool.

Change `VERSION.txt` file to `0.2` and rebuild the firmware. Then create a new artifact using the following command line:

```
path/to/mender-artifact write rootfs-image --compression none --device-type mender-esp32-example --artifact-name mender-esp32-example-v$(head -n1 path/to/mender-esp32-example/VERSION.txt) --output-path path/to/mender-esp32-example/build/mender-esp32-example-v$(head -n1 path/to/mender-esp32-example/VERSION.txt).mender --file path/to/mender-esp32-example/build/mender-esp32-example.bin
```

Upload the artifact `mender-esp32-example-v0.2.mender` to the mender server and create a new deployment.

The device checks for the new deployment, downloads the artifact and installs it on the next ota partition. Then it reboots to apply the update:

```
I (249310) main: Mender client connect network
I (249310) example_connect: Start example_connect.

... (wifi connecting to the network)

I (254100) example_common: Connected to example_netif_sta
I (254100) example_common: - IPv4 address: 192.168.2.140,
I (254110) example_common: - IPv6 address: fe80:0000:0000:0000:7e9e:bdff:feed:bc1c, type: ESP_IP6_ADDR_IS_LINK_LOCAL
I (254120) mender: ./components/mender-mcu-client/mender-mcu-client/core/src/mender-client.c (884): Checking for deployment...
I (254190) wifi:<ba-add>idx:0 (ifx:0, ca:fb:00:03:97:ce), tid:0, ssn:1, winSize:64
I (255140) esp-x509-crt-bundle: Certificate validated
I (256120) HTTP_CLIENT: Body received in fetch header state, 0x3ffcae18, 140
I (256120) mender: ./components/mender-mcu-client/mender-mcu-client/core/src/mender-client.c (918): Downloading deployment artifact with id '2c878cbb-3268-4aac-8fd9-9fdb07430739', artifact name 'mender-esp32-example-v0.2' and uri 'https://hosted-mender-artifacts.s3.amazonaws.com/6370b06a7f0deaedb279fb6a/8041a7d0-5db2-4223-b512-15c98eab87fb?X-Amz-Algorit
I (256570) esp-x509-crt-bundle: Certificate validated
I (257650) main: Deployment status is 'downloading'
I (258420) esp-x509-crt-bundle: Certificate validated
I (259550) mender: ./components/mender-mcu-client/mender-mcu-client/core/src/mender-artifact.c (382): Artifact has valid versionI (260170) mender: ./components/mender-mcu-client/mender-mcu-client/platform/flash/esp-idf/src/mender-flash.c (48): Start flashing artifact 'mender-esp32-example.bin' with size 931696
I (260180) mender: ./components/mender-mcu-client/mender-mcu-client/platform/flash/esp-idf/src/mender-flash.c (61): Next update 
partition is 'ota_1', subtype 17 at offset 0x210000 and with size 2031616
I (318090) esp_image: segment 0: paddr=00210020 vaddr=3f400020 size=38c98h (232600) map
I (318170) esp_image: segment 1: paddr=00248cc0 vaddr=3ffb0000 size=0328ch ( 12940) 
I (318170) esp_image: segment 2: paddr=0024bf54 vaddr=40080000 size=040c4h ( 16580) 
I (318180) esp_image: segment 3: paddr=00250020 vaddr=400d0020 size=93a4ch (604748) map
I (318380) esp_image: segment 4: paddr=002e3a74 vaddr=400840c4 size=0fccch ( 64716) 
I (318400) mender: ./components/mender-mcu-client/mender-mcu-client/core/src/mender-client.c (930): Download done, installing artifact
I (319450) esp-x509-crt-bundle: Certificate validated
I (320580) main: Deployment status is 'installing'
I (320580) esp_image: segment 0: paddr=00210020 vaddr=3f400020 size=38c98h (232600) map
I (320660) esp_image: segment 1: paddr=00248cc0 vaddr=3ffb0000 size=0328ch ( 12940) 
I (320670) esp_image: segment 2: paddr=0024bf54 vaddr=40080000 size=040c4h ( 16580) 
I (320670) esp_image: segment 3: paddr=00250020 vaddr=400d0020 size=93a4ch (604748) map
I (320870) esp_image: segment 4: paddr=002e3a74 vaddr=400840c4 size=0fccch ( 64716) 
I (321500) esp-x509-crt-bundle: Certificate validated
I (322630) main: Deployment status is 'rebooting'
I (322630) main: Mender client released network

...

I (329220) main: Restarting system

... (system is rebooting)

I (696) main: MAC address of the device '7c:9e:bd:ed:bc:1c'
I (696) main: Running project 'mender-esp32-example' version '0.2'
I (706) main: Mender client initialized
I (706) main: Mender inventory add-on registered
I (726) main: Mender client connect network
I (726) example_connect: Start example_connect.

... (wifi connecting to the network)

I (5686) example_common: Connected to example_netif_sta
I (5696) example_common: - IPv4 address: 192.168.2.140,
I (5696) example_common: - IPv6 address: fe80:0000:0000:0000:7e9e:bdff:feed:bc1c, type: ESP_IP6_ADDR_IS_LINK_LOCAL
I (7656) esp-x509-crt-bundle: Certificate validated
I (8706) HTTP_CLIENT: Body received in fetch header state, 0x3ffca4b8, 156
I (8706) main: Mender client authenticated
I (8776) mender: ./components/mender-mcu-client/mender-mcu-client/platform/flash/esp-idf/src/mender-flash.c (171): Application has been mark valid and rollback canceled
I (9296) esp-x509-crt-bundle: Certificate validated
I (10426) main: Deployment status is 'success'
I (10446) mender: ./components/mender-mcu-client/mender-mcu-client/core/src/mender-client.c (884): Checking for deployment...
I (10936) esp-x509-crt-bundle: Certificate validated
I (11866) mender: ./components/mender-mcu-client/mender-mcu-client/core/src/mender-client.c (892): No deployment available
I (11866) main: Mender client released network
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
