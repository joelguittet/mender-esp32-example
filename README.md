# mender-esp32-example

[![CI Badge](https://github.com/joelguittet/mender-esp32-example/workflows/ci/badge.svg)](https://github.com/joelguittet/mender-esp32-example/actions)
[![Issues Badge](https://img.shields.io/github/issues/joelguittet/mender-esp32-example)](https://github.com/joelguittet/mender-esp32-example/issues)
[![License Badge](https://img.shields.io/github/license/joelguittet/mender-esp32-example)](https://github.com/joelguittet/mender-esp32-example/blob/master/LICENSE)

[Mender MCU client](https://github.com/joelguittet/mender-mcu-client) is an open source over-the-air (OTA) library updater for MCU devices. This demonstration project runs on ESP32 hardware.


## Getting started

This project is used with an [ESP32-WROOM-32D](https://www.espressif.com/sites/default/files/documentation/esp32-wroom-32d_esp32-wroom-32u_datasheet_en.pdf) module with 4MB flash. It should be compatible with other ESP32 modules with no modification.

The project is built using ESP-IDF framework. There is no other dependencies. Important note: the project has been tested with ESP-IDF v5.2.x, v5.3.x and v5.4.x successfully.

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

Particularly, it is possible to activate the Device Troubleshoot add-on that will permit to display the logs of the ESP32 directly on the Mender interface as shown on the following screenshot. File Transfer feature can be activated too. A littlefs partition is used to upload/download files to/from the Mender server.

![Troubleshoot console](https://raw.githubusercontent.com/joelguittet/mender-esp32-example/master/.github/docs/troubleshoot.png)

Note this also constraints to download [esp_websocket_client](https://components.espressif.com/components/espressif/esp_websocket_client) in vscode, which is compatible with ESP-IDF v5.0 and later only (older ESP-IDF versions are no more supported by Espressif today).

### Execution of the application

After flashing the application on the ESP32 module and displaying logs, you should be able to see the following:

```
I (31) boot: ESP-IDF v5.4-690-gd4aa25a38e 2nd stage bootloader
I (31) boot: compile time Mar 18 2025 21:36:25
I (31) boot: Multicore bootloader
I (33) boot: chip revision: v1.0
I (36) boot.esp32: SPI Speed      : 40MHz
I (40) boot.esp32: SPI Mode       : DIO
I (43) boot.esp32: SPI Flash Size : 4MB
I (47) boot: Enabling RNG early entropy source...
I (52) boot: Partition Table:
I (54) boot: ## Label            Usage          Type ST Offset   Length
I (60) boot:  0 nvs              WiFi data        01 02 00009000 00008000
I (67) boot:  1 otadata          OTA data         01 00 00011000 00002000
I (74) boot:  2 phy_init         RF data          01 01 00013000 00001000
I (80) boot:  3 ota_0            OTA app          00 10 00020000 001b0000
I (87) boot:  4 ota_1            OTA app          00 11 001d0000 001b0000
I (93) boot:  5 storage          Unknown data     01 83 00380000 00080000
I (100) boot: End of partition table

... (system booting)

I (602) main_task: Started on CPU0
I (612) main_task: Calling app_main()
I (622) main: MAC address of the device '7c:9e:bd:ed:bc:1c'
I (622) main: Running project 'mender-esp32-example' version '0.1'
I (622) main: Mender client initialized
I (632) main: Mender inventory add-on registered
I (632) mender: ./components/mender-mcu-client/mender-mcu-client/platform/storage/esp-idf/nvs/src/mender-storage.c (83): Authentication keys are not available
I (652) mender: ./components/mender-mcu-client/mender-mcu-client/platform/tls/generic/mbedtls/src/mender-tls.c (118): Generating authentication keys...
I (20112) mender: ./components/mender-mcu-client/mender-mcu-client/platform/storage/esp-idf/nvs/src/mender-storage.c (157): Deployment data not available
I (20112) main: Mender client connect network
I (20122) main: Connecting to the network
I (20122) example_connect: Start example_connect.

... (wifi connecting to the network)

I (24542) example_connect: Got IPv4 event: Interface "example_netif_sta" address: 192.168.2.140
I (24622) example_connect: Got IPv6 event: Interface "example_netif_sta" address: fe80:0000:0000:0000:7e9e:bdff:feed:bc1c, type: ESP_IP6_ADDR_IS_LINK_LOCAL
I (24622) example_common: Connected to example_netif_sta
I (24632) example_common: - IPv4 address: 192.168.2.140,
I (24632) example_common: - IPv6 address: fe80:0000:0000:0000:7e9e:bdff:feed:bc1c, type: ESP_IP6_ADDR_IS_LINK_LOCAL
I (24722) main: Connected to the network
I (27172) esp-x509-crt-bundle: Certificate validated
E (28302) mender: ./components/mender-mcu-client/mender-mcu-client/core/src/mender-api.c (514): [401] Unauthorized: dev auth: unauthorized
I (28302) main: Mender client authentication failed
I (28302) main: Mender client released network
I (38312) main: Disconnecting network

... (wifi disconnecting of the network)

I (38342) main: Disconnected of the network
```

Which means you now have generated authentication keys on the device. Authentication keys are stored in NVS partition of the ESP32. You now have to accept your device on the mender interface. Once it is accepted on the mender interface the following will be displayed:

```
I (120632) main: Mender client connect network
I (120632) main: Connecting to the network
I (120632) example_connect: Start example_connect.

... (wifi connecting to the network)

I (124622) example_connect: Got IPv6 event: Interface "example_netif_sta" address: fe80:0000:0000:0000:7e9e:bdff:feed:bc1c, type: ESP_IP6_ADDR_IS_LINK_LOCAL
I (124962) esp_netif_handlers: example_netif_sta ip: 192.168.2.140, mask: 255.255.255.0, gw: 192.168.2.1
I (124962) example_connect: Got IPv4 event: Interface "example_netif_sta" address: 192.168.2.140
I (124972) example_common: Connected to example_netif_sta
I (124972) example_common: - IPv4 address: 192.168.2.140,
I (124982) example_common: - IPv6 address: fe80:0000:0000:0000:7e9e:bdff:feed:bc1c, type: ESP_IP6_ADDR_IS_LINK_LOCAL
I (125622) main: Connected to the network
I (126912) esp-x509-crt-bundle: Certificate validated
I (128032) main: Mender client authenticated
I (128042) mender: ./components/mender-mcu-client/mender-mcu-client/core/src/mender-client.c (902): Checking for deployment...
I (128542) esp-x509-crt-bundle: Certificate validated
I (129462) mender: ./components/mender-mcu-client/mender-mcu-client/core/src/mender-client.c (910): No deployment available
I (129472) main: Mender client released network
I (129472) main: Mender client connect network
I (129482) main: Connected to the network
I (129972) esp-x509-crt-bundle: Certificate validated
I (131102) main: Mender client released network
I (141102) main: Disconnecting network

... (wifi disconnecting of the network)

I (141132) main: Disconnected of the network
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
I (248042) main: Mender client connect network
I (248042) main: Connecting to the network
I (248042) example_connect: Start example_connect.

... (wifi connecting to the network)

I (252372) example_connect: Got IPv4 event: Interface "example_netif_sta" address: 192.168.2.140
I (252622) example_connect: Got IPv6 event: Interface "example_netif_sta" address: fe80:0000:0000:0000:7e9e:bdff:feed:bc1c, type: ESP_IP6_ADDR_IS_LINK_LOCAL
I (252622) example_common: Connected to example_netif_sta
I (252632) example_common: - IPv4 address: 192.168.2.140,
I (252632) example_common: - IPv6 address: fe80:0000:0000:0000:7e9e:bdff:feed:bc1c, type: ESP_IP6_ADDR_IS_LINK_LOCAL
I (252652) mender: ./components/mender-mcu-client/mender-mcu-client/core/src/mender-client.c (902): Checking for deployment...
I (252662) main: Connected to the network
I (253152) esp-x509-crt-bundle: Certificate validated
I (254092) mender: ./components/mender-mcu-client/mender-mcu-client/core/src/mender-client.c (929): Downloading deployment artifact with id '933bd469-4658-4e02-9138-eed503defc27', artifact name 'mender-esp32-example-v0.2' and uri 'https://hosted-mender-artifacts.s3.amazonaws.com/6370b06a7f0deaedb279fb6a/c84ecede-8f37-40e6-9f2f-1ec67f0f4c03?X-Amz-Algorit
I (254702) esp-x509-crt-bundle: Certificate validated
I (255832) main: Deployment status is 'downloading'
I (256542) esp-x509-crt-bundle: Certificate validated
I (258302) mender: ./components/mender-mcu-client/mender-mcu-client/core/src/mender-artifact.c (374): Artifact has valid version
I (258302) mender: ./components/mender-mcu-client/mender-mcu-client/platform/flash/esp-idf/src/mender-flash.c (40): Start flashing artifact 'mender-esp32-example.bin' with size 1168416
I (258312) mender: ./components/mender-mcu-client/mender-mcu-client/platform/flash/esp-idf/src/mender-flash.c (53): Next update partition is 'ota_1', subtype 17 at offset 0x1d0000 and with size 1769472
I (320662) esp_image: segment 0: paddr=001d0020 vaddr=3f400020 size=3e794h (255892) map
I (320752) esp_image: segment 1: paddr=0020e7bc vaddr=3ff80000 size=0001ch (    28) 
I (320752) esp_image: segment 2: paddr=0020e7e0 vaddr=3ffb0000 size=01838h (  6200) 
I (320762) esp_image: segment 3: paddr=00210020 vaddr=400d0020 size=c2b24h (797476) map
I (321032) esp_image: segment 4: paddr=002d2b4c vaddr=3ffb1838 size=02afch ( 11004) 
I (321032) esp_image: segment 5: paddr=002d5650 vaddr=40080000 size=17dach ( 97708) 
I (321072) mender: ./components/mender-mcu-client/mender-mcu-client/core/src/mender-client.c (941): Download done, installing artifact
I (321672) esp-x509-crt-bundle: Certificate validated
I (322802) main: Deployment status is 'installing'
I (322802) esp_image: segment 0: paddr=001d0020 vaddr=3f400020 size=3e794h (255892) map
I (322892) esp_image: segment 1: paddr=0020e7bc vaddr=3ff80000 size=0001ch (    28) 
I (322892) esp_image: segment 2: paddr=0020e7e0 vaddr=3ffb0000 size=01838h (  6200) 
I (322902) esp_image: segment 3: paddr=00210020 vaddr=400d0020 size=c2b24h (797476) map
I (323172) esp_image: segment 4: paddr=002d2b4c vaddr=3ffb1838 size=02afch ( 11004) 
I (323182) esp_image: segment 5: paddr=002d5650 vaddr=40080000 size=17dach ( 97708) 
I (323722) esp-x509-crt-bundle: Certificate validated
I (324852) main: Deployment status is 'rebooting'
I (324852) main: Mender client released network
I (324852) main: Disconnecting network

... (wifi disconnecting of the network)

I (324892) main: Disconnected of the network
I (334902) main: Restarting system

... (system is rebooting)

I (698) main_task: Started on CPU0
I (708) main_task: Calling app_main()
I (758) main: LittleFS partition size: total: 524288, used: 143360
I (758) main: MAC address of the device '7c:9e:bd:ed:bc:1c'
I (768) main: Running project 'mender-esp32-example' version '0.2'
I (768) main: Mender client initialized
I (778) mender: ./components/mender-mcu-client/mender-mcu-client/platform/storage/esp-idf/nvs/src/mender-storage.c (220): Device configuration not available
I (788) main: Mender configure add-on registered
I (798) main: Mender inventory add-on registered
I (798) main: Mender troubleshoot add-on registered
I (808) main: Device configuration retrieved
I (818) main: Mender client connect network
I (818) main: Connecting to the network
I (818) example_connect: Start example_connect.

... (wifi connecting to the network)

I (4758) example_connect: Got IPv6 event: Interface "example_netif_sta" address: fe80:0000:0000:0000:7e9e:bdff:feed:bc1c, type: ESP_IP6_ADDR_IS_LINK_LOCAL
I (5218) esp_netif_handlers: example_netif_sta ip: 192.168.2.140, mask: 255.255.255.0, gw: 192.168.2.1
I (5218) example_connect: Got IPv4 event: Interface "example_netif_sta" address: 192.168.2.140
I (5218) example_common: Connected to example_netif_sta
I (5228) example_common: - IPv4 address: 192.168.2.140,
I (5238) example_common: - IPv6 address: fe80:0000:0000:0000:7e9e:bdff:feed:bc1c, type: ESP_IP6_ADDR_IS_LINK_LOCAL
I (5758) main: Connected to the network
I (7048) esp-x509-crt-bundle: Certificate validated
I (8168) main: Mender client authenticated
I (8238) mender: ./components/mender-mcu-client/mender-mcu-client/platform/flash/esp-idf/src/mender-flash.c (163): Application has been mark valid and rollback canceled
I (8678) esp-x509-crt-bundle: Certificate validated
I (9768) main: Deployment status is 'success'
I (9778) mender: ./components/mender-mcu-client/mender-mcu-client/core/src/mender-client.c (902): Checking for deployment...
I (10318) esp-x509-crt-bundle: Certificate validated
I (11238) mender: ./components/mender-mcu-client/mender-mcu-client/core/src/mender-client.c (910): No deployment available
I (11248) main: Mender client released network
I (11248) main: Mender client connect network
I (11482) main: Connected to the network
I (11972) esp-x509-crt-bundle: Certificate validated
I (13102) main: Mender client released network
I (13102) main: Disconnecting network

... (wifi disconnecting of the network)

I (13132) main: Disconnected of the network
```

Congratulation! You have updated the device. Mender server displays the success of the deployment.

### Failure or wanted rollback

In case of failure to connect and authenticate to the server the current example application performs a rollback to the previous release.
You can customize the behavior of the example application to add your own checks and perform the rollback in case the tests fail.

### Using Device Troubleshoot add-on

The Device Troubleshoot add-on permits to display the ESP-IDF console on the Mender interface. Autocompletion and colors are available.

The Device Troubleshoot add-on also permits to upload/download files to/from the Mender server. The littlefs partition mounted at `/littlefs` is used to demonstrate this feature. To send a file to the device, destination path must start with `/littlefs`. To download a file from the device the full path is expected, starting with `/littlefs`.

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


## License

Copyright joelguittet and mender-mcu-client contributors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
