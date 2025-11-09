import time
import os
from textwrap import wrap
import subprocess
from app.services.whisper_service import transcribe_and_diarize
from app.services.summarizer_service import CHUNK_PROMPT, MERGE_PROMPT, llama_summarize
from app.services.pdf_service import generate_pdf

#Function to ensure the audio file is in WAV format(best format for whisper)
def ensure_wav(audio_path: str) -> str:
    if audio_path.lower().endswith(".wav"):
        return audio_path# Already in WAV format

    wav_path = os.path.splitext(audio_path)[0] + ".wav"
    try:
        print(f"Converting {audio_path} → {wav_path}", flush=True)
        # Run ffmpeg command to convert the file into a single-channel 16kHz WAV file
        subprocess.run(
            ["ffmpeg", "-y", "-i", audio_path, "-ac", "1", "-ar", "16000", wav_path],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return wav_path
    except Exception as e:
        print(f" Audio conversion error : {e}", flush=True)
        raise RuntimeError(f"WAV conversion failed for {audio_path}")

#Main pipeline: Transcription → Summarization → PDF generation
def generate_report(audio_path: str):
    try:
        # Step 1: Convert to WAV format if needed
        audio_path = ensure_wav(audio_path)
        # Step 2: Transcribe the audio and detect speakers + language
        whisper_segments, speaker_segments, detected_language, _ = transcribe_and_diarize(audio_path)
    except Exception as e:
        print(f"Error during transcription/diarization : {e}", flush=True)
        return {"error": "Transcription or diarization failed."}

    if not whisper_segments:
        return {"error": "No transcription detected."}

    # Step 3: Merge transcribed text with detected speakers
    print("Merging transcriptions with speakers..", flush=True)
    final_transcript = []
    try:
        for ws in whisper_segments:
            #Find speakers 
            speakers = [s["speaker"] for s in speaker_segments
                        if not (ws["end"] < s["start"] or ws["start"] > s["end"])]
            speaker = speakers[0] if speakers else "Unknown"
            final_transcript.append(f"[{speaker}] {ws['text']}")
    except Exception as e:
        print(f"Error while merging text and speaker segments: {e}", flush=True)
        return {"error": "Failed to merge text and speakers."}
    # Combine all lines into a single transcript string
    transcription_text = "\n".join(final_transcript)
    # Extract the list of participants(speakers)
    participants = sorted(set(s["speaker"] for s in speaker_segments if s["speaker"] != "Unknown"))

    if not participants:
        print("No participants detected.", flush=True)

    # Step 4: Summarization in chunks
    print(f"Summarizing in {detected_language}...", flush=True)
    # Split long transcripts into smaller parts for better summarization performance
    chunks = wrap(transcription_text, 1500 if len(transcription_text) > 4000 else 4000)
    summaries = []
    
    for i, chunk in enumerate(chunks, 1):
        try:
            # Prepare the summarization prompt with the chunk content
            prompt = CHUNK_PROMPT.format(
                chunk=chunk, 
                participants=', '.join(participants),
                language=detected_language
            )
            print(f"Processing chunk {i}/{len(chunks)}", flush=True)
            # Call the LLM to summarize the current chunk
            summaries.append(llama_summarize(prompt))
            # delay to avoid overloading the model or API
            if i < len(chunks):
                time.sleep(2)
        except Exception as e:
            print(f"Error summarizing chunk {i} : {e}", flush=True)
    # If no summaries were successfully generated, return an error
    if not summaries:
        return {"error": "No summaries generated."}

    # Step 5: Merge all partial summaries into a single final summary
    try:
        joined_parts = "\n\n".join([f"--- Partie {i+1} ---\n{s}" for i, s in enumerate(summaries)])
        merged_prompt = MERGE_PROMPT.format(
            participants=', '.join(participants),
            parts=joined_parts,
            language=detected_language
        )
        final_summary = llama_summarize(merged_prompt)
    except Exception as e:
        print(f" Error during final summary merge: {e}", flush=True)
        return {"error": "Failed to merge summaries."}

    # Step 6: Generate the final PDF report
    try:
        pdf_path = generate_pdf(final_summary, participants)
    except Exception as e:
        print(f" Error generating PDF: {e}", flush=True)
        pdf_path = None

    return {
        "summary": final_summary,
        "pdf_path": pdf_path,
        "participants": participants,
        "language": detected_language
    }