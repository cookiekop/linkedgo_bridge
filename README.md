
# Linkedgo Bridge Integration for Home Assistant

[English](./README.md) | [简体中文](./README_zh.md)

<p align="left">
  <img src="http://smartspeaker.linked-go.com/iotapplet-image/ha_logo.png" alt="linkedgo" title="linkedgo" la="la">
</p>

Linekdgo Bridge Integration is officially supported by linkedgo company. It allows you to control your linkedgo devices in Home Assistant. Currently, it has already supported thomerstate (ST830, ST1800HN, ST2000).


## Installation

> Home Assistant version requirement:
>
> - Core >= 2024.4.4
> - Operating System >= 13.0


### Method: [HACS](https://hacs.xyz/) Community Store

HACS > In the search box, type **Linkedgo Bridge** > Click **Linkedgo Bridge**, getting into the detail page > Click **DOWNLOAD** in bottom-right corner of the page

After the installation completes successfully, a message will prompt you to reboot the system.
Go to Settings > System, then click the Reboot button in the upper-right corner.
Once the system restarts, proceed to the **Linkedgo Bridge** configuration.

## Integration Configuration

### Linkedgo APP
1. Download linkedgo app from IOS store or Google store.
2. Register your linkedgo account by Phone number or E-mail.
3. Create a house
4. Add devices to your house following the app's instructions and assgin a region and a room to each device.

### Linkedgo Bridge configuration
1. Settings > Devices & services 
2. ADD INTEGRATION
3. In the search box, type **Linkedgo Bridge**
4. Click here to login > Sign in with Linkedgo App account


### Add Linkedgo Devices

After logging in successfully, a dialog box named "Select House and Devices" pops up. You can select the House containing the device that you want to import in Home Assistant.


[Instruction](./specification.md)
