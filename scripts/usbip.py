#!/usr/bin/env python3
# @file      usbip.py
# @brief     Attach or detach a remote USB device using USB/IP
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

import argparse
import glob
import os
import re
import shutil
import socket
import subprocess
import sys
import platform
from urllib.parse import urlparse


def find_usbip():
    """Locate the usbip executable."""
    candidates = glob.glob("/usr/lib/linux-tools/*/usbip")

    # Prefer the directory matching the running kernel version.
    kernel_version = platform.release()
    preferred = f"/usr/lib/linux-tools/{kernel_version}/usbip"

    if os.path.isfile(preferred) and os.access(preferred, os.X_OK):
        return preferred

    # Fall back to another installed linux-tools version.
    candidates.sort(reverse=True)

    for candidate in candidates:
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate

    # Fall back to PATH.
    candidate = shutil.which("usbip")
    if candidate:
        return candidate

    sys.exit(
        "Error: usbip executable not found. Searched "
        "/usr/lib/linux-tools/*/usbip and PATH."
    )


USBIP = find_usbip()


def run_command(command):
    """Run a command and return its standard output."""
    try:
        result = subprocess.run(
            command,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError:
        print(
            f"Error: command not found: {command[0]}",
            file=sys.stderr,
        )
        sys.exit(1)
    except subprocess.CalledProcessError as exc:
        if exc.stdout:
            print(exc.stdout, end="", file=sys.stderr)
        if exc.stderr:
            print(exc.stderr, end="", file=sys.stderr)
        sys.exit(exc.returncode)

    return result.stdout


def resolve_addresses(host):
    """Resolve a hostname to IP addresses."""
    try:
        return {
            result[4][0]
            for result in socket.getaddrinfo(
                host, None, type=socket.SOCK_STREAM
            )
        }
    except socket.gaierror:
        return set()


def hosts_match(requested, actual):
    """Compare hostnames or IP addresses."""
    if requested.lower() == actual.lower():
        return True

    return bool(resolve_addresses(requested) & resolve_addresses(actual))


def compile_location_regex(location_regex):
    """Compile the location regex or report a useful error."""
    try:
        return re.compile(location_regex)
    except re.error as exc:
        sys.exit(f"Error: invalid location regex: {exc}")


def discover_remote_devices(remote):
    """Return (bus_id, description) pairs exported by the remote host."""
    output = run_command([USBIP, "list", "-r", remote])
    devices = []

    # Example:
    # 1-2.3: STMicroelectronics : ST-LINK/V2.1 (0483:374b)
    pattern = re.compile(r"^\s*(\d+-[\d.]+):\s*(.*)$")

    for line in output.splitlines():
        match = pattern.match(line)
        if match:
            devices.append(
                (match.group(1), match.group(2).strip())
            )

    return devices


def ensure_vhci_loaded():
    """Load the USB/IP virtual host controller module if necessary."""
    if not os.path.exists("/sys/module/vhci_hcd"):
        print("Loading vhci_hcd...")
        run_command(["modprobe", "vhci_hcd"])


def attach(location_regex, remote):
    """Find and attach a matching remote device."""
    location = compile_location_regex(location_regex)

    devices = discover_remote_devices(remote)
    matches = [
        (bus_id, description)
        for bus_id, description in devices
        if location.search(bus_id)
    ]

    if not matches:
        sys.exit(
            f"Error: no exported device on {remote} matches "
            f"location regex {location_regex!r}"
        )

    if len(matches) > 1:
        details = "\n".join(
            f"  {bus_id}: {description}"
            for bus_id, description in matches
        )
        sys.exit(f"Error: multiple matching devices found:\n{details}")

    bus_id, description = matches[0]

    print(f"Using USB/IP executable: {USBIP}")

    ensure_vhci_loaded()

    run_command([USBIP, "attach", "-r", remote, "-b", bus_id])
    print(f"🔌 Attached device {bus_id}: {description} from {remote}")


def detach(location_regex, remote):
    """Find and detach an imported device matching host and bus ID."""
    location = compile_location_regex(location_regex)

    output = run_command([USBIP, "port"])
    matches = []

    # Split output into blocks, one per local USB/IP port.
    blocks = re.split(
        r"(?=^\s*Port\s+\d+:)",
        output,
        flags=re.MULTILINE,
    )

    for block in blocks:
        port_match = re.search(
            r"^\s*Port\s+(\d+):",
            block,
            re.MULTILINE,
        )

        if not port_match:
            continue

        # Example:
        # 5-1 -> usbip://192.168.3.20:3240/1-2.3
        for line in block.splitlines():
            match = re.search(
                r"usbip://([^/\s]+)/([0-9]+-[\d.]+)",
                line,
            )

            if not match:
                continue

            endpoint, bus_id = match.groups()
            host = urlparse("//" + endpoint).hostname

            if (
                host
                and location.search(bus_id)
                and hosts_match(remote, host)
            ):
                matches.append(
                    (port_match.group(1), bus_id, host)
                )

    if not matches:
        sys.exit(
            f"Error: no attached device from {remote} matches "
            f"location regex {location_regex!r}"
        )

    if len(matches) > 1:
        details = "\n".join(
            f"  port {port}, remote bus {bus_id}, host {host}"
            for port, bus_id, host in matches
        )
        sys.exit(
            f"Error: multiple matching attached devices found:\n{details}"
        )

    port, bus_id, host = matches[0]

    print(f"Using USB/IP executable: {USBIP}")

    run_command([USBIP, "detach", "-p", port])
    print(f"🔌 Detached device {host}/{bus_id} from local port {port}")


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Attach or detach a remote USB/IP device "
            "by matching its bus ID with a regex."
        )
    )

    parser.add_argument(
        "action",
        choices=("attach", "detach"),
        help="Whether to attach or detach the device",
    )
    parser.add_argument(
        "location",
        help=r"Regex matching the USB bus ID, e.g. '[0-9]-2\.3'",
    )

    args = parser.parse_args()

    remote = os.getenv("BOARD_FARM_ADDRESS")

    if args.action == "attach":
        attach(args.location, remote)
    else:
        detach(args.location, remote)


if __name__ == "__main__":
    main()
