# Glucose Didgeridoo

A simple data sonification script that generates musical drones from blood glucose data retrieved from a Dexcom CGM (or continuous glucose monitor) in MIDI. Based heavily on [pydexcom](https://github.com/gagebenne/pydexcom)

## Instructions

1. Make sure **Dexcom Share** is enabled on your account. You do not need to set up followers but this must be enabled so that the Dexcom API can access your glucose data.

2. Create a .env file with the following variables:

* *DEXCOM_USERNAME*: Your Dexcom username
* *DEXCOM_PASSWORD*: Your Dexcom password
* *PORT*: The MIDI port the musical data will be sent to: (default: "Microsoft GS Wavetable Synth 0")
* *INTERVAL*: The length of the drone generated in seconds (default: 8, although your Dexcom updates every 300)
* *SYNTH_RELEASE*: The length of the selected synth's release envelope in milliseconds (default: 10)

These are all important for the software to function. I'll be working on a version with args and other more intuitive configuration methods.

3. If you want to use this MIDI data with a DAW or other software on your PC, you will need to create a virtual MIDI port. You can use software like [LoopMIDI](https://www.tobias-erichsen.de/software/loopmidi.html) to achieve this. Set your PORT in .env to the name of your generated port.

4. Simply run the script

```bash
python main.py
```

## TO-DO

* Args implementation
  * Args for synth release, note interval and MIDI port
  * Chord customisation for each trend
* Self-generate virtual MIDI port
* Generate MIDI file of generated notes
* Improved error handling

## License

This project is under the MIT License.
