# Denkovi smartDEN IP Devices

Home Assistant custom integration for Denkovi network-connected I/O devices.

## Features

- Only JSON is used for communication with the devices.
- Devices:
  - smartDEN IP-16R: 16 relay
  - smartDEN IP-32IN: 16 digital input binary sensors, 8 analog input sensors and 8 temperature input sensors.
- UI-based setup and configuration
- Reads all states on configurable polling interval (default 30 seconds)
- Status of all relays is returned and refreshed every time that any relay is toggled.
- Asynchronous network I/O and Home Assistant data update coordinator.

## Not going to support

- SNMP protocol because it's very different from http-based protocols
- XML and HTML will only be supported for features and devices where a JSON endpoint is not available
- Encrypted passwords because enabling that option disables Multiple Access feature on the device

## Security

These devices are **extremely insecure** and are **NOT** suitable for exposing on the publict internet NOR in untrusted local networks (like schools or cafes).  
This integration's communication method with devices is therefore also considered extremely insecure.
We recommends using these devices ONLY on isolated VLANs so they can't be exploited by unauthorized users or rogue IoT devices on the same network.

Device's API is written in such a way that it requires the password in the query string.  
Traffic is not encrypted, and URLs (including password) may be recorded in device, proxy logs or Homeassistant logs.  
Use an isolated network and do not expose the device's HTTP interface to the Internet.

There isn't much we can do to improve this in the integration itself.

## Installation

### HACS

1. Publish this repository to GitHub.
2. In HACS, add it as a custom repository of category **Integration**.
3. Install **Denkovi smartDEN IP Devices** and restart Home Assistant.

## Configuration

Go to **Settings → Devices & services → Add integration → Denkovi smartDEN IP Devices**.
Enter the device host, HTTP port, password, model and polling interval.

On Denkovi's smartDEN devices enable the JSON API and ensure the "Encrypt Password" option is disabled.
Integration sends the password as the `pw` query parameter on every request, matching the device API
request format.

