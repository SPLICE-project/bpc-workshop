## ESP Thermometer
This implemetation uses the VS Code extention [PlatformIO](https://platformio.org/) and is based on [this](https://randomnerdtutorials.com/esp32-ds18b20-temperature-arduino-ide/) tutorial. 

If you wish to modify just import the [ESP32Therm](../ESP32Therm/) directory as project into PlatformIO. Note that to flash the ESP 32 drivers for the specific board need to be installed on your computer. [Here](https://www.silabs.com/interface/usb-bridges/classic/device.cp2102?tab=softwareandtools) is a link if you are using the same developing borad as us (see **Hardware Components** below)

This implemtation relies on the following git repositories (added as git submodules):
* [OneWire](https://github.com/PaulStoffregen/OneWire)
* [Arduino Temepature Control Library](https://github.com/milesburton/Arduino-Temperature-Control-Library)

To clone this repository with its submodules:
```bash
git clone --recursive <repository-url>
```
Alternatively, if you have already clone this repo the submodules can be fetched as follows:
```bash
cd bpc-ccny24-demos
git submodule update --init
```

# Hardware Components
* [DS18B20 Digital Temperature Sensor (Waterproof)](https://www.amazon.com/BOJACK-Temperature-Waterproof-Stainless-Raspberry/dp/B09NVWNGLQ/ref=asc_df_B09NVWNGLQ/?tag=hyprod-20&linkCode=df0&hvadid=647322370067&hvpos=&hvnetw=g&hvrand=5845084728042350873&hvpone=&hvptwo=&hvqmt=&hvdev=c&hvdvcmdl=&hvlocint=&hvlocphy=9002419&hvtargid=pla-1641936078130&psc=1&mcid=5d0a3757f83e30579948ec213679b327/)
* [DOIT ESP32 DEVKIT](https://makeradvisor.com/tools/esp32-dev-board-wi-fi-bluetooth/)
