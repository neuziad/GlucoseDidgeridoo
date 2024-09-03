from pydexcom import Dexcom
import time
import mido
import argparse
from apscheduler.schedulers.background import BackgroundScheduler
from mido import MidiFile, MidiTrack, Message, bpm2tempo

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Glucose Digeridoo: Dexcom Glucose to MIDI")
parser.add_argument("--username", type=str, required=True, help="Dexcom username")
parser.add_argument("--password", type=str, required=True, help="Dexcom password (must be written in single quotes)")
parser.add_argument("--port", type=str, default="Microsoft GS Wavetable Synth 0", help="MIDI port data is sent to (must be written in single quotes)")
parser.add_argument("--bpm", type=int, default=80, help="BPM for scheduling glucose readings and MIDI notes")
parser.add_argument("--release", type=int, default=10, help="Release time of synthesizer (in milliseconds)")
parser.add_argument("--list-ports", action='store_true', help='List available MIDI output ports')
parser.add_argument("--output-midi", type=str, help='Path to save the generated MIDI file (optional)')

args = parser.parse_args()

# Variables from command-line arguments
username = args.username
password = args.password
port_used = args.port
bpm = args.bpm
release = args.release
output_midi = args.output_midi

# List ports option
if args.list_ports:
    print("======== Available MIDI ports ========")
    for port in mido.get_output_names():
        print(f'{port}')
    print("======================================")
    exit()

# Open virtual MIDI port
print(f"Starting script...")
midi_out = mido.open_output(port_used)

# Retrieve information from API and set up scheduler
dexcom = Dexcom(username=username, password=password, ous=True)
scheduler = BackgroundScheduler()

# Calculate the duration of one bar in seconds
seconds_per_beat = 60 / bpm
bar_duration = seconds_per_beat * 4  # Assuming 4/4 time signature

# Create a new MIDI file and track if output_midi is specified
# if output_midi:
ticks_per_beat = 480  # Default ticks per beat
midi_file = MidiFile(ticks_per_beat=ticks_per_beat)
midi_track = MidiTrack()
midi_file.tracks.append(midi_track)
midi_track.append(mido.MetaMessage('set_tempo', tempo=bpm2tempo(bpm)))

# Function that maps glucose readings to MIDI notes
def data_to_midi(glucose_value):
    min_glucose = 20
    max_glucose = 400
    min_midi = 36
    max_midi = 108

    # Normalize values
    midi_note = int(min_midi + (glucose_value - min_glucose) * (max_midi - min_midi) / (max_glucose - min_glucose))
    midi_note = max(min_midi, min(midi_note, max_midi))  
    return midi_note

# Function that retrieves glucose information
def fetch_glucose(counter=[-1]):
    glucose_reading = dexcom.get_current_glucose_reading()

    try:
        glucose_value = glucose_reading.value
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
    print(f"Date and time of current reading taken: {glucose_reading.datetime.strftime('%d/%m/%Y, %H:%M:%S')}")
    print(f"Glucose trending: {glucose_trend.capitalize()} {glucose_reading.trend_arrow}")
    print(f"MIDI Note: {midi_note}")

    # Determine chord and notes
    if glucose_trend == "rising quickly":
        notes = [midi_note, midi_note + 4, midi_note + 8] # Augemented triad when increasing rapidly
        print(f"Chord played: {note_name}aug")
    if glucose_trend == "rising":
        notes = [midi_note, midi_note + 3, midi_note + 6] # Diminished triad when increasing gradually
        print(f"Chord played: {note_name}dim")
    if glucose_trend == "rising slightly":
        notes = [midi_note, midi_note + 4, midi_note + 7] # Major triad when increasing slightly
        print(f"Chord played: {note_name}")
    if glucose_trend == "steady":
        notes = [midi_note, midi_note + 7, midi_note + 12] # Perfect fifth when stable
        print(f"Chord played: {note_name}5")
    if glucose_trend == "falling slightly":
        notes = [midi_note, midi_note + 3, midi_note + 7] # Minor chord when decreasing slightly
        print(f"Chord played: {note_name}m")
    if glucose_trend == "falling":
        notes = [midi_note - 5, midi_note, midi_note + 6] # 2nd inversion of major 7th suspended 2nd chord when decreasing gradually
        print(f"Chord played: {note_name}maj7sus2")
    if glucose_trend == "falling quickly":
        notes = [midi_note - 1, midi_note, midi_note + 8] # Dissonant chord when decreasing rapidly
        print(f"Chord played: {note_name}6sus(b2)")
    if glucose_trend == "trend unavailable":
        notes = [midi_note] # If no trend, just play the root note
        print(f"Chord played: {note_name} note")

    print(f"Octave: {octave}")

    # Calculate note duration in ticks based on the bar duration
    note_duration_ticks = int(midi_file.ticks_per_beat * 4)  # Entire bar duration in ticks

    # Send MIDI messages and log them
    for note in notes:
        midi_out.send(Message('note_on', note=note, velocity=64))
        if output_midi:
            midi_track.append(Message('note_on', note=note, velocity=64, time=0))  # Add to MIDI file

    time.sleep(bar_duration - (release/1000))  # Wait for the duration of the bar

    for note in notes:
        midi_out.send(Message('note_off', note=note, velocity=64))
        if output_midi:
            midi_track.append(Message('note_off', note=note, velocity=64, time=note_duration_ticks))  # Add to MIDI file

# Scheduler
def start_scheduler():
    scheduler.add_job(fetch_glucose, 'interval', seconds=bar_duration, max_instances=3)
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
        # Save MIDI file if path is specified
        if output_midi:
            midi_file.save(output_midi)
            print(f"MIDI file saved as {output_midi}")
