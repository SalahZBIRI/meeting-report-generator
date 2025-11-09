import torch
from faster_whisper import WhisperModel
from pyannote.audio import Pipeline

#Function to transcribe speech and identify speakers in an audio file
def transcribe_and_diarize(audio_path: str):
    """Transcrit et segmente les locuteurs depuis un fichier audio."""
    print("Transcribing audio with Whispe...", flush=True)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device.upper()}", flush=True)


    # Load a lightweight Whisper model for transcription
    model = WhisperModel("small", device=device)
    # Perform the transcription
    segments, info = model.transcribe(audio_path)

    detected_language = info.language
    language_probability = info.language_probability
    print(f"Detected language: : {detected_language}", flush=True)
    # Convert the transcription segments into a clean, structured format
    whisper_segments = [{"start": s.start, "end": s.end, "text": s.text.strip()} for s in segments]

    print("Initializing Pyannote speaker diarization pipeline...", flush=True)
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1")
    # Run the diarization to detect speaker turns
    diarization = pipeline({"audio": audio_path})
    # Convert diarization results into a list of speaker segments
    speaker_segments = [
        {"start": turn.start, "end": turn.end, "speaker": speaker}
        for turn, _, speaker in diarization.itertracks(yield_label=True)
    ]
    #Return the Whisper transcription and the Pyannote speaker segments
    return whisper_segments, speaker_segments, detected_language, language_probability