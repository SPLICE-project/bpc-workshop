# Cloning this repo

This repository depends on other repositories added as git submodules:
* [OneWire](https://github.com/PaulStoffregen/OneWire)
* [Arduino Temepature Control Library](https://github.com/milesburton/Arduino-Temperature-Control-Library)

To get the submodules necessary for the **man-in-the-middle** attack, make sure the repository is cloned as follows:
```bash
git clone --recursive <repository-url>
```
Alternatively, if you have already clone this repo the submodules can be fetched as follows:
```bash
cd bpc-ccny24-demos
git submodule update --init
```