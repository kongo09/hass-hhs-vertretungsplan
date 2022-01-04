[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)


## Support Heinrich-Hertz-Schule, Hamburg, Vertretungsplan in Home Assistant

### Note:

* This integration only makes sense to you, if your kid is attending the Heinrich-Hertz-Schule in Hamburg, Germany
* You will need a user name and a password to access the data. Please ask your Elternvertreter.
    
  
## Setup

### Installation:
* Go to HACS -> Integrations
* Click the three dots on the top right and select `Custom Repositories`
* Enter `https://github.com/kongo09/hass-hhs-vertretungsplan` as repository, select the category `Integration` and click Add
* A new custom integration shows up for installation (HHS Vertretungsplan) - install it
* Restart Home Assistant
  
  
### Configuration:
* Go to Configuration -> Integrations
* Click `Add Integration`
* Search for `HHS Vertretungsplan` and select it
* Specify the class your kid is attending
* Add your user name and password
  
  
## Usage:

### Devices:

The integration provides the Heinrich-Hertz-Schule as a device to Home Assistant
  
  
### Entities:

| Entity ID                      | Type               |  Description                                                               |
|--------------------------------|--------------------|----------------------------------------------------------------------------|
| binary_sensor.hhs_today_7f     | Binary Sensor      |  Is on, if there is Vertretung today, for 7f. See attributes for details   |
