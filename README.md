# Amazon Tethered BL Unlock
![License](https://img.shields.io/github/license/R0rt1z2/amazon-tethered-unlock)
![GitHub release (latest by date including pre-releases)](https://img.shields.io/github/v/release/R0rt1z2/amazon-tethered-unlock?include_prereleases)
![GitHub Issues](https://img.shields.io/bitbucket/issues-raw/R0rt1z2/amazon-tethered-unlock?color=red)

Simple Python(3) script to disable LK verification in Amazon Preloader images and boot/recovery image verification in Amazon LK ("Little Kernel") images.

## Requirements
* Python 3.9 (or newer).
* Preloader &/or LK from an amazon device.

## Notice
* Use this tool at your own risk. I am not responsible for bricked devices. Please **BACKUP** your PL/LK before using this tool.
* Please **do not redistribute images** that have been modified with this tool as after all, all images are property of MediaTek Inc and Amazon.
* When reporting an issue, provide a detailed report (Android Version, device, and attach both images).

## Usage
```
patcher.py [pl|lk] <input file> <output file>
```

## Supported versions
* [x] Android 5.1.
* [x] Android 7.1.
* [ ] Android 9.

## License
* This tool is licensed under the GNU (v3) General Public License. See `LICENSE` for more details.

