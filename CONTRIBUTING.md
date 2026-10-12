# Contributing

## How it works

Denkovi smartDEN devices expose their current state via a JSON API and allow control using rudimentary JSON commands.  
The integration interacts with this API using HTTP requests. For example, to retrieve the current state:

`GET /current_state.json?pw=PASSWORD`

Relay changes on the IP-16R use `RelayN=0` or `RelayN=1` query parameters, for example
`/current_state.json?pw=PASSWORD&Relay1=1`.

For IP-32IN, the integration reads `CurrentState.DigitalInput`, `AnalogInput`, and
`TemperatureInput` arrays from `/current_state.json`. Digital inputs become binary
sensors. Analog inputs expose the device's numeric `Value` (raw 10-bit reading) and retain its
human-readable `Measure` string as an entity attribute. Temperature inputs expose their
numeric `Value`; a device value such as `---` is exposed as unavailable rather than
converted to a fabricated number.

## Development and validation

Repository includes GitHub Actions for Home Assistant hassfest, HACS validation and Megalinter + pytest.  
All checks must pass in CI before publication.

Model-specific protocol support belongs in `api.py` or a dedicated model driver.
Do not add a model until its JSON request/response format has been verified against its manual and preferably tested against real hardware.

## Relevant Documentation

[Denkovi smartDEN IP-16R Manual](https://denkovi.com/Documents/smartDen-IP-16R/Current-Version/UserManual.pdf)
[Denkovi smartDEN IP-32IN Manual](https://denkovi.com/Documents/smartDen-IP-32IN/Current-Version/smartDEN-IP-32IN.pdf)