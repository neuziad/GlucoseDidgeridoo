from pydexcom import Dexcom
import os
from dotenv import load_dotenv
import time
from apscheduler.schedulers.background import BackgroundScheduler
import mido
load_dotenv()

# Importing Dexcom user information for credentials
username = os.getenv("DEXCOM_USERNAME")
password = os.getenv("DEXCOM_PASSWORD")

# Importing settings for script from .env file
port_used = os.getenv("PORT") # MIDI port used for output
interval = int(os.getenv("INTERVAL")) # Interval between glucose readings recorded (in seconds)
release = int(os.getenv("SYNTH_RELEASE")) # Release time of synthesizer (in milliseconds)

# Default options for non-Dexcom settings
if port_used == None:
    port_used = "Microsoft GS Wavetable Synth 0"
if interval == None:
    interval = 8
if release == None:
    release = 10

# Open virtual MIDI port
print(f"Starting script...")
midi_out = mido.open_output(port_used)

# Retrieve information from API and set up scheduler
dexcom = Dexcom(username=username, password=password, ous=True)
scheduler = BackgroundScheduler()

# Function that maps glucose readings to MIDI notes
def data_to_midi(glucose_value):
    min_glucose = 20
    max_glucose = 400
    min_midi = 36
    max_midi = 108

    # Normalise values
    midi_note = int(min_midi + (glucose_value - min_glucose) * (max_midi - min_midi) / (max_glucose - min_glucose))
    midi_note = max(min_midi, min(midi_note, max_midi))  
    return midi_note

# Function that retrieves glucose information
def fetch_glucose(counter=[-1]):
    glucose_reading = dexcom.get_current_glucose_reading()

    try:
        glucose_value = glucose_reading.value # Set glucose reading to mg/dL rather than mmol/L, the standard in the UK and the one I happen to use most
    except AttributeError:
        print("No glucose reading available at the moment.")
        return
    
    # Increment the counter
    counter[0] += 1

    # Get the trend of the glucose
    glucose_trend = glucose_reading.trend_description

    midi_note = data_to_midi(glucose_value)

    # Converting MIDI note number to note
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    note_name = note_names[midi_note % 12]
    octave = (midi_note // 12) - 1

    # Printing information
    print(f"======== GLUCOSE NOTE INFORMATION {counter[0]} ========")
    print(f"Current blood glucose: {glucose_value} mg/dL")
    print(f"Date and time of current reading taken: {glucose_reading.datetime.strftime("%d/%m/%Y, %H:%M:%S")}")
    print(f"Glucose trending: {glucose_trend.capitalize()} {glucose_reading.trend_arrow}")
    print(f"MIDI Note: {midi_note}")

    if glucose_trend == "rising quickly":
        notes = [midi_note, midi_note + 4, midi_note + 8] # Augemented triad when increasing rapidly
        print(f"Chord played: {note_name}aug")
        print(f"Octave: {octave}")
    if glucose_trend == "rising":
        notes = [midi_note, midi_note + 3, midi_note + 6] # Diminished triad when increasing gradually
        print(f"Chord played: {note_name}dim")
        print(f"Octave: {octave}")
    if glucose_trend == "rising slightly":
        notes = [midi_note, midi_note + 4, midi_note + 7] # Major triad when increasing slightly
        print(f"Chord played: {note_name}")
        print(f"Octave: {octave}")
    if glucose_trend == "steady":
        notes = [midi_note, midi_note + 7, midi_note + 12] # Perfect fifth when stable
        print(f"Chord played: {note_name}5")
        print(f"Octave: {octave}")
    if glucose_trend == "falling slightly":
        notes = [midi_note, midi_note + 3, midi_note + 7] # Minor chord when decreasing slightly
        print(f"Chord played: {note_name}m")
        print(f"Octave: {octave}")
    if glucose_trend == "falling":
        notes = [midi_note - 5, midi_note, midi_note + 6] # 2nd inversion of major 7th suspended 2nd chord when decreasing gradually
        print(f"Chord played: {note_name}maj7sus2")
        print(f"Octave: {octave}")
    if glucose_trend == "falling quickly":
        notes = [midi_note - 1, midi_note, midi_note + 8] # Dissonant chord when decreasing rapidly
        print(f"Chord played: {note_name}6sus(b2)")
        print(f"Octave: {octave}")
    if glucose_trend == "trend unavailable":
        print(f"Chord played: {note_name} note")
        print(f"Octave: {octave}")
        notes = [midi_note] # If no trend, just play the root note

    for note in notes:
        midi_out.send(mido.Message('note_on', note=note, velocity=64))

    time.sleep(interval - (release/1000))

    for note in notes:
        midi_out.send(mido.Message('note_off', note=note, velocity=64))

# Scheduler
def start_scheduler():
    scheduler.add_job(fetch_glucose, 'interval', seconds=interval, max_instances=3)
    scheduler.start()

def stop_scheduler():
    scheduler.shutdown()

if __name__ == "__main__":
    start_scheduler()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"================= END INFO =================")
        print("Stopping script...")
        stop_scheduler()