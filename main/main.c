/**
 * @file      main.c
 * @brief     Main entry point
 *
 * MIT License
 *
 * Copyright (c) 2022-2023 joelguittet and mender-mcu-client contributors
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

#include <stdio.h>
#include "esp_event.h"
#include "esp_log.h"
#include "esp_mac.h"
#include "esp_ota_ops.h"
#include "freertos/FreeRTOS.h"
#include "freertos/event_groups.h"
#include "freertos/task.h"
#include "mender-client.h"
#include "mender-inventory.h"
#include "mender-ota.h"
#include "nvs_flash.h"
#include "protocol_examples_common.h"
#include "sdkconfig.h"

/**
 * @brief Tag used for logging
 */
static const char *TAG = "main";

/**
 * @brief Mender client events
 */
static EventGroupHandle_t mender_client_events;
#define MENDER_CLIENT_EVENT_RESTART (1 << 0)

/**
 * @brief Authentication success callback
 * @return MENDER_OK if application is marked valid and success deployment status should be reported to the server, error code otherwise
 */
static mender_err_t
authentication_success_cb(void) {

    mender_err_t ret;

    ESP_LOGI(TAG, "Mender client authenticated");

    /* Activate mender add-ons */
    /* The application can activate each add-on depending of the current status of the device */
    /* In this example, add-ons are activated has soon as authentication succeeds */
#ifdef CONFIG_MENDER_CLIENT_ADD_ON_INVENTORY
    if (MENDER_OK != (ret = mender_inventory_activate())) {
        ESP_LOGE(TAG, "Unable to activate inventory add-on");
        return ret;
    }
#endif /* CONFIG_MENDER_CLIENT_ADD_ON_INVENTORY */

    /* Validate the image if it is still pending */
    /* Note it is possible to do multiple diagnosic tests before validating the image */
    /* In this example, authentication success with the mender-server is enough */
    if (MENDER_OK != (ret = mender_ota_mark_app_valid_cancel_rollback())) {
        ESP_LOGE(TAG, "Unable to validate the image");
        return ret;
    }

    return ret;
}

/**
 * @brief Authentication failure callback
 * @return MENDER_OK if nothing to do, error code if the mender client should restart the application
 */
static mender_err_t
authentication_failure_cb(void) {

    static int   tries = 0;
    mender_err_t ret   = MENDER_OK;

    /* Increment number of failures */
    tries++;
    ESP_LOGI(TAG, "Mender client authentication failed (%d/%d)", tries, CONFIG_EXAMPLE_AUTHENTICATION_FAILS_MAX_TRIES);

    /* Invalidate the image if it is still pending */
    /* Note it is possible to invalid the image later to permit clean closure before reboot */
    /* In this example, several authentication failures with the mender-server is enough */
    if (tries >= CONFIG_EXAMPLE_AUTHENTICATION_FAILS_MAX_TRIES) {
        if (MENDER_OK != (ret = mender_ota_mark_app_invalid_rollback_and_reboot())) {
            ESP_LOGE(TAG, "Unable to invalidate the image");
            return ret;
        }
    }

    return ret;
}

/**
 * @brief Deployment status callback
 * @param status Deployment status value
 * @param desc Deployment status description as string
 * @return MENDER_OK if the function succeeds, error code otherwise
 */
static mender_err_t
deployment_status_cb(mender_deployment_status_t status, char *desc) {

    /* We can do something else if required */
    ESP_LOGI(TAG, "Deployment status is '%s'", desc);

    return MENDER_OK;
}

/**
 * @brief Restart callback
 * @return MENDER_OK if the function succeeds, error code otherwise
 */
static mender_err_t
restart_cb(void) {

    /* Application is responsible to shutdown and restart the system now */
    xEventGroupSetBits(mender_client_events, MENDER_CLIENT_EVENT_RESTART);

    return MENDER_OK;
}

#if configUSE_TRACE_FACILITY == 1

/**
 * @brief Print FreeRTOS stats
 */
static void
print_stats(void) {

    /* Take a snapshot of the number of tasks in case it changes while this function is executing */
    volatile UBaseType_t uxArraySize = uxTaskGetNumberOfTasks();

    /* Allocate a TaskStatus_t structure for each task */
    TaskStatus_t *pxTaskStatusArray = pvPortMalloc(uxArraySize * sizeof(TaskStatus_t));
    if (NULL != pxTaskStatusArray) {

        /* Generate raw status information about each task */
        uxArraySize = uxTaskGetSystemState(pxTaskStatusArray, uxArraySize, NULL);

        /* For each populated position in the pxTaskStatusArray array, format the raw data as human readable ASCII data */
        printf("--------------------------------------------------------\n");
        printf("Task Name       | Stack High Water Mark\n");
        printf("--------------------------------------------------------\n");
        for (UBaseType_t index = 0; index < uxArraySize; index++) {
            printf("%15s | %u bytes\n", pxTaskStatusArray[index].pcTaskName, pxTaskStatusArray[index].usStackHighWaterMark * sizeof(configSTACK_DEPTH_TYPE));
        }

        /* Release memory */
        vPortFree(pxTaskStatusArray);
    }

    /* Print usage of the heap */
    printf("--------------------------------------------------------\n");
    printf("Free Heap Size: %u bytes\n", xPortGetFreeHeapSize());
    printf("Minimum Ever Free Heap Size: %u bytes\n", xPortGetMinimumEverFreeHeapSize());
    printf("--------------------------------------------------------\n");
}

#endif /* configUSE_TRACE_FACILITY == 1 */

/**
 * @brief Main function
 */
void
app_main(void) {

    /* Initialize NVS */
    esp_err_t ret = nvs_flash_init();
    if ((ESP_ERR_NVS_NO_FREE_PAGES == ret) || (ESP_ERR_NVS_NEW_VERSION_FOUND == ret)) {
        ESP_LOGI(TAG, "Erasing flash...");
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);

    /* Initialize network */
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());

    /* 
     * This helper function configures Wi-Fi or Ethernet, as selected in menuconfig.
     * Read "Establishing Wi-Fi or Ethernet Connection" section in
     * examples/protocols/README.md for more information about this function.
     */
    ESP_ERROR_CHECK(example_connect());

    /* Read base MAC address of the ESP32 */
    uint8_t mac[6];
    char    mac_address[18];
    ESP_ERROR_CHECK(esp_base_mac_addr_get(mac));
    sprintf(mac_address, "%02x:%02x:%02x:%02x:%02x:%02x", mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);

    /* Create mender-client event group */
    mender_client_events = xEventGroupCreate();
    ESP_ERROR_CHECK(NULL == mender_client_events);

    /* Retrieve running version of the ESP32 */
    esp_app_desc_t         running_app_info;
    const esp_partition_t *running = esp_ota_get_running_partition();
    ESP_ERROR_CHECK(esp_ota_get_partition_description(running, &running_app_info));
    ESP_LOGI(TAG, "Running project '%s' version '%s'", running_app_info.project_name, running_app_info.version);

    /* Compute artifact name */
    char artifact_name[128];
    sprintf(artifact_name, "%s-v%s", running_app_info.project_name, running_app_info.version);

    /* Retrieve device type */
    char *device_type = running_app_info.project_name;

    /* Initialize mender-client */
    mender_client_config_t    mender_client_config    = { .mac_address                  = mac_address,
                                                    .artifact_name                = artifact_name,
                                                    .device_type                  = device_type,
                                                    .host                         = CONFIG_MENDER_SERVER_HOST,
                                                    .tenant_token                 = CONFIG_MENDER_SERVER_TENANT_TOKEN,
                                                    .authentication_poll_interval = CONFIG_MENDER_CLIENT_AUTHENTICATION_POLL_INTERVAL,
                                                    .update_poll_interval         = CONFIG_MENDER_CLIENT_UPDATE_POLL_INTERVAL,
                                                    .recommissioning              = false };
    mender_client_callbacks_t mender_client_callbacks = { .authentication_success = authentication_success_cb,
                                                          .authentication_failure = authentication_failure_cb,
                                                          .deployment_status      = deployment_status_cb,
                                                          .ota_begin              = mender_ota_begin,
                                                          .ota_write              = mender_ota_write,
                                                          .ota_abort              = mender_ota_abort,
                                                          .ota_end                = mender_ota_end,
                                                          .ota_set_boot_partition = mender_ota_set_boot_partition,
                                                          .restart                = restart_cb };
    ESP_ERROR_CHECK(mender_client_init(&mender_client_config, &mender_client_callbacks));
    ESP_LOGI(TAG, "Mender client initialized");

    /* Initialize mender add-ons */
#ifdef CONFIG_MENDER_CLIENT_ADD_ON_INVENTORY
    mender_inventory_config_t mender_inventory_config
        = { .artifact_name = artifact_name, .device_type = device_type, .poll_interval = CONFIG_MENDER_CLIENT_INVENTORY_POLL_INTERVAL };
    ESP_ERROR_CHECK(mender_inventory_init(&mender_inventory_config));
    ESP_LOGI(TAG, "Mender inventory initialized");
#endif /* CONFIG_MENDER_CLIENT_ADD_ON_INVENTORY */

#ifdef CONFIG_MENDER_CLIENT_ADD_ON_INVENTORY
    /* Set mender inventory (this is just an example) */
    mender_inventory_t inventory[]
        = { { .name = "latitude", .value = "45.8325" }, { .name = "longitude", .value = "6.864722" }, { .name = NULL, .value = NULL } };
    if (MENDER_OK != mender_inventory_set(inventory)) {
        ESP_LOGE(TAG, "Unable to set mender inventory");
    }
#endif /* CONFIG_MENDER_CLIENT_ADD_ON_INVENTORY */

    /* Infinite loop, print stats periodically */
    EventBits_t event = 0;
    while (!event) {

#if configUSE_TRACE_FACILITY == 1
        /* Print stats */
        print_stats();
#endif /* configUSE_TRACE_FACILITY == 1 */

        /* Wait before next snapshot or the application shutdown */
        event = xEventGroupWaitBits(mender_client_events, MENDER_CLIENT_EVENT_RESTART, pdTRUE, pdFALSE, 10000 / portTICK_PERIOD_MS);
    }

    /* Release mender add-ons */
#ifdef CONFIG_MENDER_CLIENT_ADD_ON_INVENTORY
    mender_inventory_exit();
#endif /* CONFIG_MENDER_CLIENT_ADD_ON_INVENTORY */

    /* Exit mender-client */
    mender_client_exit();

    /* Release event group */
    vEventGroupDelete(mender_client_events);

    /* Restart */
    ESP_LOGI(TAG, "Restarting system");
    esp_restart();
}
