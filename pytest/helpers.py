# @file      helpers.py
# @brief     Helpers
#
# Copyright joelguittet and mender-mcu-client contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import re
import pexpect
import subprocess
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from pytest_embedded import Dut


class Helpers:
    """
    Provides helper methods for device management.
    """

    def get_device_mac_address(self, dut: Dut, timeout=60) -> str:
        try:
            m = dut.expect(pattern=r"MAC address of the device '(?P<mac>[0-9A-Za-z:]+)'", timeout=timeout)
        except pexpect.TIMEOUT:
            raise AssertionError("🔴​​​ MAC address of the device not found")
        mac_address = m.group('mac').decode()
        print(f"🔵​ MAC address of the device is '{mac_address}'")
        return mac_address

    def get_device_firmware_version(self, dut: Dut, project_name: str, timeout=60) -> str:
        try:
            m = dut.expect(pattern=rf"Running project '{project_name}' version '(?P<version>[0-9.+]+)'", timeout=timeout)
        except pexpect.TIMEOUT:
            raise AssertionError("🔴​​​ Firmware version of the device not found")
        fw_version = m.group('version').decode()
        print(f"🔵​ Firmware version of the device is '{fw_version}'")
        return fw_version

    def assert_device_not_authenticated(self, dut: Dut, timeout=600):
        try:
            m = dut.expect(pattern=r"(?P<expected>.*E.*\[401\] Unauthorized.*)|(?P<not_expected>.*I.*Mender client authenticated.*)", timeout=timeout)
        except pexpect.TIMEOUT:
            raise AssertionError("🔴​​​ Device is not communicating with the server")
        if not m.group('expected') or m.group('not_expected'):
            raise AssertionError("🔴​​​ Device is authenticated to the server but it should not")
        print("✅ Device is not authenticated")

    def assert_device_authenticated(self, dut: Dut, timeout=600):
        try:
            m = dut.expect(pattern=r"(?P<not_expected>.*E.*\[401\] Unauthorized.*)|(?P<expected>.*I.*Mender client authenticated.*)", timeout=timeout)
        except pexpect.TIMEOUT:
            raise AssertionError("🔴​​​ Device is not communicating with the server")
        if not m.group('expected') or m.group('not_expected'):
            raise AssertionError("🔴​​​ Device is not authenticated to the server but it should")
        print("✅ Device is authenticated")

    def assert_device_troubleshoot_connected(self, dut: Dut, timeout=600):
        try:
            dut.expect(pattern="Troubleshoot client connected", timeout=timeout)
        except pexpect.TIMEOUT:
            raise AssertionError("🔴​​​ Device troubleshoot doesn't appear to be connected but it should")
        print("✅ Device troubleshoot connected")

    def create_mender_artifact(self, build_dir: Path, device_type: str, artifact_name_prefix: str, version: str) -> Path:
        # Create artifact using mender-artifact
        esp_idf_signed_bin = Path(build_dir) / "mender-esp32-example.bin"
        artifact_file = Path(build_dir) / f"{artifact_name_prefix}-v{version}.mender"
        cmd = f"mender-artifact write rootfs-image --compression none --device-type {device_type} --artifact-name {artifact_name_prefix}-v{version} --output-path {artifact_file} --file {esp_idf_signed_bin}"
        subprocess.run(cmd, shell=True, check=True)
        return artifact_file

    def run_until_data_refreshed(self, f, timeout=600, interval=30):
        start_time = time.time()
        while time.time() - start_time < timeout:
            data, updated_ts = f()
            if data is not None and updated_ts is not None:
                delta = interval * 2
                if datetime.fromisoformat(updated_ts) > datetime.now(timezone.utc) - timedelta(seconds=delta):
                    return data
            time.sleep(interval)
        return None

    def run_until_data_available(self, f, timeout=600, interval=30):
        start_time = time.time()
        while time.time() - start_time < timeout:
            data = f()
            if data is not None:
                return data
            time.sleep(interval)
        return None
