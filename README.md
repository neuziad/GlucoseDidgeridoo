# Glucose Didgeridoo

A simple data sonification script that generates musical drones from blood glucose data retrieved from a Dexcom CGM (or continuous glucose monitor) in MIDI. Based heavily on [pydexcom](https://github.com/gagebenne/pydexcom) and so works with the **Dexcom G4, G5 and G6** (There are issues with how the G7 authenticates user information, which I will address in a future update). The glucose level is mapped to a specific note from C2 to C8, while the trend of the glucose pattern is mapped to the type of chord played.

This software can be used to generate sonifications of your glucose trend in the form of ambient drones. Feel free to transform this code to your looking, whether you're looking for more data-accurate sonifications or as a tool to create interesting musical patterns and ideas with your glucose information!

## Instructions

1. Make sure **Dexcom Share** is enabled on your account. You do not need to set up followers but this must be enabled so that the Dexcom API can access your glucose data.

2. If you want to use this MIDI data with a DAW or other software on your PC, you will need to create a virtual MIDI port. You can use software like [LoopMIDI](https://www.tobias-erichsen.de/software/loopmidi.html) to achieve this. Set your PORT in .env to the name of your generated port.

3. Simply run the script with your Dexcom log-in information:

```bash
python glucosedidgeridoo.py --username [DEXCOM_EMAIL] --password '[DEXCOM_PASSWORD]'
```

Replace [DEXCOM_EMAIL] and [DEXCOM_PASSWORD] with the respective email and password associated with your Dexcom account. Password must be in single quotes.

Additionally, you can specify the MIDI port the data is sent to, the length between each data point recorded and the release envelope of the synth you're using with these arguments:

```bash
[--port 'MIDI_PORT'] [--interval INTERVAL] [--release RELEASE] 
```

Port specified must be in single quotes. Interval and release must be integers.

You can see which ports are available to use with this command:

```bash
python glucosedidgeridoo.py --username [DEXCOM_EMAIL] --password '[DEXCOM_PASSWORD]' --list-ports
```

## TO-DO

* Args implementation
  * Chord customisation for each trend
* Self-generate virtual MIDI port
* Generate MIDI file of generated notes
* Improved error handling
* Save session to MIDI
* Save log
* G7 integration
* Rhythm mode: create unique polyrhythmic patterns with glucose information, as opposed to tonal drones.

## License

This project is under the MIT License.
