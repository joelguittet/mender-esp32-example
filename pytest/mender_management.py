# @file      mender_management.py
# @brief     Mender management API wrapper
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

import json
import os
import requests
import time
from datetime import datetime, timezone
from requests.auth import HTTPBasicAuth


class MenderManagement:
    """
    Wrapper around Mender Management API (v1/v2).
    Provides methods for device management, inventory, configuration and deployments.
    """

    def __init__(self,
                 server=None,
                 username=None,
                 password=None,
                 ca_cert=None):
        self.server = server or os.getenv("MENDER_SERVER", "https://mender.mycompany.local")
        self.username = username or os.getenv("MENDER_USERNAME", "admin@mycompany.local")
        self.password = password or os.getenv("MENDER_PASSWORD", "MySecretPassword")
        self.ca_cert = ca_cert or os.getenv("MENDER_CA", "/etc/ssl/certs/my-ca.crt")

        self.token = None
        self.headers = None
        self.login()

    def _request(self, method, url, **kwargs):
        retry = True
        while True:
            try:
                r = requests.request(method=method, url=url, headers=self.headers, verify=self.ca_cert, timeout=10, **kwargs)
                r.raise_for_status()
                return r
            except requests.exceptions.HTTPError as e:
                if r.status_code == 401 and retry:
                    print(f"🟡 HTTP error occurred: {e}")
                    try:
                        print(f"🟡 Server response: {r.json()}")
                    except ValueError:
                        print(f"🟡 Server response: {r.text}")
                    print("🟡 Authentication expired, logging in again and retrying...")
                    self.login()
                    retry = False
                    continue
                print(f"🔴 HTTP error occurred: {e}")
                try:
                    print(f"🔴 Server response: {r.json()}")
                except ValueError:
                    print(f"🔴 Server response: {r.text}")
                raise
            except requests.exceptions.RequestException as e:
                print(f"🔴 Network error occurred: {e}")
                raise

    # ============================================================
    # AUTH
    # ============================================================
    def login(self):
        # Authenticate to Mender Management API using Basic Auth or JSON body.
        url = f"{self.server}/api/management/v1/useradm/auth/login"

        try:
            resp = requests.post(url, auth=HTTPBasicAuth(self.username, self.password), verify=self.ca_cert, timeout=10)
            if resp.status_code == 200 and resp.text.strip():
                self.token = resp.text.strip()
                self.headers = {"Authorization": f"Bearer {self.token}"}
                print("✅ Mender Management logged in with Basic Auth")
                return
        except requests.RequestException:
            pass

        try:
            resp = requests.post(url, json={"username": self.username, "password": self.password}, verify=self.ca_cert, timeout=10)
            resp.raise_for_status()
            if resp.text.strip():
                self.token = resp.text.strip()
                self.headers = {"Authorization": f"Bearer {self.token}"}
                print("✅ Mender Management logged in with JSON body")
                return
        except requests.RequestException as e:
            raise RuntimeError(f"🔴​ Login failed (Basic + JSON): {e}") from e

    # ============================================================
    # DEVICES
    # ============================================================
    def list_devices(self):
        # Return all devices known by Mender.
        url = f"{self.server}/api/management/v2/devauth/devices"
        r = self._request("GET", url)
        return r.json() if r.text else {}

    def get_device_by_mac(self, mac_address):
        # Return a single device and auth_set by MAC address.
        devices = self.list_devices()
        for device in devices:
            try:
                identity_data = device.get('identity_data')
                # Handle both JSON string and dict cases
                if isinstance(identity_data, str):
                    identity = json.loads(identity_data)
                elif isinstance(identity_data, dict):
                    identity = identity_data
                else:
                    continue
                if identity.get('mac') == mac_address:
                    return device
            except (KeyError, json.JSONDecodeError):
                continue
        return None

    def accept_device(self, device):
        # Accept device.
        auth_sets = device.get('auth_sets', [])
        auth = auth_sets[0] if auth_sets else None
        url = f"{self.server}/api/management/v2/devauth/devices/{device['id']}/auth/{auth['id']}/status"
        payload = {"status": "accepted"}
        self._request("PUT", url, json=payload)
        return True

    def delete_device(self, device):
        # Delete device.
        url = f"{self.server}/api/management/v2/devauth/devices/{device['id']}"
        self._request("DELETE", url)
        return True

    # ============================================================
    # INVENTORY
    # ============================================================
    def get_device_inventory(self, device):
        # Retrieve current inventory data for a device.
        url = f"{self.server}/api/management/v1/inventory/devices/{device['id']}"
        r = self._request("GET", url)
        return r.json() if r.text else {}

    # ============================================================
    # CONFIGURATION
    # ============================================================
    def get_device_configuration(self, device):
        # Retrieve current configuration data for a device.
        url = f"{self.server}/api/management/v1/deviceconfig/configurations/device/{device['id']}"
        r = self._request("GET", url)
        return r.json() if r.text else {}

    def set_device_configuration(self, device, configuration):
        # Set configuration key/values for a device.
        url = f"{self.server}/api/management/v1/deviceconfig/configurations/device/{device['id']}"
        self._request("PUT", url, json=configuration)
        return True

    def deploy_device_configuration(self, device):
        # Deploy configuration key/values for a device.
        url = f"{self.server}/api/management/v1/deviceconfig/configurations/device/{device['id']}/deploy"
        payload = {"retries": 0}
        r = self._request("POST", url, json=payload)
        return r.json() if r.text else {}

    # ============================================================
    # DEPLOYMENTS
    # ============================================================
    def upload_artifact(self, filepath, description=None):
        # Upload a new artifact (deployment package).
        url = f"{self.server}/api/management/v1/deployments/artifacts"
        with open(filepath, "rb") as file:
            files = {"artifact": file}
            data = {"description": description} if description else {}
            r = self._request("POST", url, files=files, data=data)
            return r.json() if r.text else {}

    def list_artifacts(self, name=None):
        # List artifacts.
        url = f"{self.server}/api/management/v1/deployments/artifacts/list"
        params = {}
        if name is not None:
            params['name'] = name
        r = self._request("GET", url, params=params)
        return r.json() if r.text else {}

    def delete_artifact(self, name):
        # Delete artifact.
        artifacts = self.list_artifacts(name)
        for artifact in artifacts:
            if artifact.get('name') == name:
                break
        url = f"{self.server}/api/management/v1/deployments/artifacts/{artifact['id']}"
        self._request("DELETE", url)
        return True

    def deploy_device_firmware(self, name, artifact_name, devices):
        # Create a deployment for one or more devices.
        url = f"{self.server}/api/management/v1/deployments/deployments"
        payload = {"name": name, "artifact_name": artifact_name, "devices": [device['id'] for device in devices]}
        r = self._request("POST", url, json=payload)
        return r.json() if r.text else {}

    def get_deployment_status(self, name=None, deployment=None):
        # Get status of a deployment.
        url = f"{self.server}/api/management/v2/deployments/deployments"
        params = {}
        if name is not None:
            params['name'] = name
        if deployment is not None and deployment.get('deployment_id') is not None:
            params['id'] = deployment['deployment_id']
        r = self._request("GET", url, params=params)
        for item in r.json():
            if name is not None:
                if item.get('name') == name:
                    return item
            if deployment is not None and deployment.get('deployment_id') is not None:
                if item.get('id') == deployment['deployment_id']:
                    return item
        return None

    def wait_for_deployment(self, name=None, deployment=None, timeout=1200, interval=30):
        # Wait until deployment completes or fails.
        deployment_status = None
        start_time = time.time()
        while time.time() - start_time < timeout:
            deployment_status = self.get_deployment_status(name, deployment)
            print(f"🔵 Device deployment status at {datetime.now(timezone.utc)} is: {deployment_status}")
            if deployment_status is not None and deployment_status.get('status') == 'finished':
                return deployment_status
            time.sleep(interval)
        return deployment_status

    def stop_deployment(self, deployment_status):
        # Abord deployment.
        url = f"{self.server}/api/management/v1/deployments/deployments/{deployment_status['id']}/status"
        payload = {"status": "aborted"}
        self._request("PUT", url, json=payload)
        return True
