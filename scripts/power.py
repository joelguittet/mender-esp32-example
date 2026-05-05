#!/usr/bin/env python3
# @file      power.py
# @brief     Control power of boards through a remotely connected USB hub
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
import shlex
import subprocess
import sys


def ssh_command(remote_args: list[str]) -> list[str]:
    """Build an SSH command and safely quote its remote command arguments."""
    server = os.getenv("BOARD_FARM_ADDRESS")
    username = os.getenv("BOARD_FARM_USERNAME")
    password = os.getenv("BOARD_FARM_PASSWORD")

    remote_command = " ".join(shlex.quote(arg) for arg in remote_args)
    return [
        "sshpass", "-p", password,
        "ssh", "-o", "StrictHostKeyChecking=no",
        f"{username}@{server}", remote_command,
    ]


def discover_hubs() -> list[tuple[str, str]]:
    """Return (location, VID:PID) pairs reported by remote uhubctl."""
    result = subprocess.run(
        ssh_command(["sudo", "/usr/sbin/uhubctl"]),
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Example:
    # Current status for hub 1-2.4 [05e3:0608, USB 2.00, 4 ports, ...]
    pattern = re.compile(
        r"^Current status for hub\s+(\S+)\s+\[([0-9a-fA-F]{4}:[0-9a-fA-F]{4})\b",
        re.MULTILINE,
    )
    return [
        (match.group(1), match.group(2).lower())
        for match in pattern.finditer(result.stdout)
    ]


def resolve_location(location_regex: str, vid_pid: str) -> str:
    """Resolve a location regex to exactly one hub with the requested VID:PID."""
    try:
        pattern = re.compile(location_regex)
    except re.error as exc:
        raise ValueError(
            f"Invalid location regex {location_regex!r}: {exc}"
        ) from exc

    hubs = discover_hubs()
    matches = [
        location
        for location, discovered_vid_pid in hubs
        if discovered_vid_pid == vid_pid.lower()
        and pattern.fullmatch(location)
    ]

    if not matches:
        available = [
            f"{location} ({discovered_vid_pid})"
            for location, discovered_vid_pid in hubs
            if discovered_vid_pid == vid_pid.lower()
        ]
        raise RuntimeError(
            f"No hub with VID:PID {vid_pid} matches location regex "
            f"{location_regex!r}. Matching hub locations found by discovery: "
            f"{', '.join(available) if available else 'none'}"
        )

    if len(matches) > 1:
        raise RuntimeError(
            f"Location regex {location_regex!r} matches multiple "
            f"{vid_pid} hubs: {', '.join(matches)}. Use a more specific regex."
        )

    return matches[0]


def parse_port_spec(spec: str) -> tuple[str, str]:
    """Split a location.port specification at its final dot."""
    try:
        location_regex, port = spec.rsplit(".", 1)
    except ValueError as exc:
        raise ValueError(
            f"Invalid port specification {spec!r}; "
            "expected <location-regex>.<port>"
        ) from exc

    if not location_regex or not port:
        raise ValueError(
            f"Invalid port specification {spec!r}; "
            "expected <location-regex>.<port>"
        )

    if not port.isdigit() or int(port) < 1:
        raise ValueError(f"Invalid port number {port!r} in {spec!r}")

    return location_regex, port


def run_uhubctl(
    location_regex: str, port: str, vid_pid: str, action: str
) -> None:
    location = resolve_location(location_regex, vid_pid)

    print(
        f"🔌 Power {action.upper()} device using hub location {location}, "
        f"port {port} (requested {location_regex}.{port})"
    )

    subprocess.run(
        ssh_command([
            "sudo", "/usr/sbin/uhubctl",
            "-l", location,
            "-p", port,
            "-a", action,
        ]),
        check=True,
    )


def main() -> int:
    if len(sys.argv) < 4:
        print(
            "Usage: power.py <on|off> <vid:pid> "
            "<location-regex>.<port> [<location-regex>.<port> ...]\n"
            "Examples:\n"
            "  power.py on 05e3:0608 '1-2.3'\n"
            "  power.py off 05e3:0608 '1-2.4.1'\n"
            "  power.py on 05e3:0608 '[0-9]-2.4.1'",
            file=sys.stderr,
        )
        return 1

    action = sys.argv[1]
    if action not in ("on", "off"):
        print(
            f"Invalid action {action!r}; expected 'on' or 'off'.",
            file=sys.stderr,
        )
        return 1

    vid_pid = sys.argv[2].lower()
    if not re.fullmatch(r"[0-9a-f]{4}:[0-9a-f]{4}", vid_pid):
        print(
            f"Invalid VID:PID {sys.argv[2]!r}; "
            "expected format 'hhhh:hhhh'.",
            file=sys.stderr,
        )
        return 1

    try:
        ports = [parse_port_spec(arg) for arg in sys.argv[3:]]

        if action == "on":
            for location_regex, port in ports:
                run_uhubctl(location_regex, port, vid_pid, "on")
        else:
            for location_regex, port in reversed(ports):
                run_uhubctl(location_regex, port, vid_pid, "off")

    except (subprocess.CalledProcessError, RuntimeError, ValueError) as exc:
        print(f"USB power operation failed: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
