import streamlit as st
import subprocess
import whisper
import os
import sys
import yt_dlp

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer

# Add FFmpeg to PATH if available
FFMPEG_PATH = r"D:\ffmpeg\ffmpeg-master-latest-win64-gpl\bin"
if os.path.exists(FFMPEG_PATH):
    if FFMPEG_PATH not in os.environ.get('PATH', ''):
        os.environ['PATH'] = FFMPEG_PATH + os.pathsep + os.environ.get('PATH', '')

st.set_page_config(page_title="YouTube Video Summarizer", layout="centered")

st.title(" YouTube Video → Summary (Open Source)")
st.write("Paste a YouTube link and get summarized text")

# Add debug information
with st.expander("Debug Information"):
    st.write(f"**Python version:** {sys.version}")
    st.write(f"**Current working directory:** {os.getcwd()}")
    st.write(f"**Temp directory exists:** {os.path.exists('temp')}")
    
    # Check yt-dlp module
    try:
        st.write(f"**yt-dlp version:** {yt_dlp.version.__version__}")
        st.success("yt-dlp module loaded successfully")
    except ImportError:
        st.error(f" yt-dlp module not found! Please install with: pip install yt-dlp")
    except Exception as e:
        st.error(f" Error with yt-dlp: {e}")
    
    # Check whisper
    try:
        import whisper
        st.write("Whisper module available")
    except ImportError:
        st.error("Whisper not found! Please install with: pip install openai-whisper")
    
    # Check FFmpeg (optional - for better audio format support)
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            st.write("FFmpeg available")
        else:
            st.warning(" FFmpeg might not be working properly")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        st.warning(" FFmpeg not installed (optional - app works fine without it)")
        st.info("To install FFmpeg:")
        st.info("1. Download from: https://ffmpeg.org/download.html")
        st.info("2. Or use: pip install ffmpeg-python")
    except Exception as e:
        st.warning(f" Error checking FFmpeg: {e}")

YOUTUBE_URL = st.text_input("🔗 Paste YouTube URL")

os.makedirs("temp", exist_ok=True)

def download_audio(url):
    """Download audio from YouTube URL using yt-dlp Python module."""
    try:
        # Use absolute paths
        temp_dir = os.path.abspath("temp")
        os.makedirs(temp_dir, exist_ok=True)
        
        # Clean up any existing audio files
        for f in os.listdir(temp_dir):
            if f.startswith("audio."):
                try:
                    os.remove(os.path.join(temp_dir, f))
                except:
                    pass
        
        # Configure yt-dlp options
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(temp_dir, 'audio.%(ext)s'),  # Use absolute path
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'extractor_retries': 5,
            'fragment_retries': 5,
            'socket_timeout': 60,
            'http_headers': {
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
                'Accept-Encoding': 'gzip, deflate',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            },
            'skip_unavailable_fragments': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            st.info(f"Downloading audio from: {url}")
            
            # Extract info first
            try:
                info = ydl.extract_info(url, download=False)
                st.info(f"Video title: {info.get('title', 'Unknown')}")
                duration = info.get('duration', 0)
                if duration:
                    minutes, seconds = divmod(duration, 60)
                    st.info(f"Duration: {int(minutes):02d}:{int(seconds):02d}")
            except Exception as info_error:
                st.warning(f"Could not extract video info: {info_error}")
            
            # Download the audio
            ydl.download([url])
        
        # Find the downloaded audio file
        audio_files = [f for f in os.listdir(temp_dir) if f.startswith("audio.")]
        
        if not audio_files:
            raise FileNotFoundError("Audio file was not created in temp directory")
        
        audio_file = audio_files[0]
        audio_path = os.path.join(temp_dir, audio_file)
        
        st.success(f"Audio downloaded successfully")
        file_size = os.path.getsize(audio_path) / 1024 / 1024
        st.info(f"File: {audio_file} ({file_size:.2f} MB)")
        st.info(f"Full path: {audio_path}")
        
        return audio_path
                
    except yt_dlp.utils.DownloadError as e:
        error_msg = f"yt-dlp download error: {str(e)}"
        st.error(error_msg)
        st.error("This might be due to:")
        st.error("1. Video is age-restricted or private")
        st.error("2. YouTube is blocking requests (try again later)")
        st.error("3. Video is not available in your region")
        st.error("4. Network connectivity issues")
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f"Unexpected error during audio download: {str(e)}"
        st.error(error_msg)
        import traceback
        st.error(traceback.format_exc())
        raise Exception(error_msg)

def validate_youtube_url(url):
    """Validate if the URL is a valid YouTube URL."""
    youtube_patterns = [
        "youtube.com/watch?v=",
        "youtu.be/",
        "youtube.com/embed/",
        "youtube.com/v/",
        "m.youtube.com/watch?v="
    ]
    return any(pattern in url.lower() for pattern in youtube_patterns)

def transcribe_audio(audio_path):
    """Transcribe audio using Whisper. Handles different audio formats."""
    try:
        # Check if file exists
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found at: {audio_path}")
        
        st.info(f"Audio file confirmed at: {audio_path}")
        st.info(f"File size: {os.path.getsize(audio_path) / 1024 / 1024:.2f} MB")
        
        # Get file extension
        _, ext = os.path.splitext(audio_path)
        st.info(f"Audio format: {ext.lower()}")
        
        # Load whisper model
        st.info("Loading Whisper model (this may take a moment)...")
        model = whisper.load_model("base")
        
        # Transcribe
        st.info("Transcribing audio...")
        result = model.transcribe(audio_path)
        
        return result["text"]
        
    except FileNotFoundError as e:
        st.error(f"File not found error: {str(e)}")
        raise Exception(f"Audio file error: {str(e)}")
    except Exception as e:
        st.error(f"Transcription error: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        raise Exception(f"Transcription failed: {str(e)}")

def summarize_text(text, sentences=5):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LexRankSummarizer()
    summary = summarizer(parser.document, sentences)
    return " ".join(str(sentence) for sentence in summary)

def get_word_count(text):
    """Count words in text"""
    return len(text.split())

def create_download_content(transcript, summary):
    """Create formatted content for download"""
    content = f"""YOUTUBE VIDEO TRANSCRIPTION & SUMMARY
=====================================

TRANSCRIPT
----------
Word Count: {get_word_count(transcript)} words

{transcript}

=====================================

SUMMARY
-------
Word Count: {get_word_count(summary)} words

{summary}

=====================================
Generated using YouTube Video Summarizer
"""
    return content

if st.button("🚀 Generate Summary"):
    if not YOUTUBE_URL:
        st.warning("Please paste a YouTube URL")
    elif not validate_youtube_url(YOUTUBE_URL):
        st.error("Please provide a valid YouTube URL")
    else:
        try:
            with st.spinner("Downloading audio..."):
                audio_file = download_audio(YOUTUBE_URL)

            with st.spinner("Transcribing audio..."):
                transcript = transcribe_audio(audio_file)

            with st.spinner("Summarizing text..."):
                summary = summarize_text(transcript)

            st.success("Done!")

            # Transcript section
            st.subheader("📜 Transcript")
            transcript_words = get_word_count(transcript)
            st.info(f"📊 Word Count: **{transcript_words} words**")
            st.text_area("", transcript, height=200, disabled=True)

            # Summary section
            st.subheader("🧠 Summary")
            summary_words = get_word_count(summary)
            
            # Show reduction statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Original Words", transcript_words)
            with col2:
                st.metric("Summary Words", summary_words)
            with col3:
                reduction_percent = ((transcript_words - summary_words) / transcript_words * 100) if transcript_words > 0 else 0
                st.metric("Reduction", f"{reduction_percent:.1f}%")
            
            st.text_area("", summary, height=150, disabled=True)

            # Download section
            st.divider()
            st.subheader("💾 Download Options")
            
            # Create download content
            download_content = create_download_content(transcript, summary)
            
            # Audio download section
            st.markdown("**🎵 Audio File:**")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                with open(audio_file, 'rb') as audio_data:
                    st.download_button(
                        label="🎵 Download Audio",
                        data=audio_data.read(),
                        file_name=os.path.basename(audio_file),
                        mime="audio/mp4" if audio_file.endswith('.m4a') else "audio/webm" if audio_file.endswith('.webm') else "audio/mpeg"
                    )
            
            st.markdown("**📄 Text Files:**")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.download_button(
                    label="📥 Download as TXT",
                    data=download_content,
                    file_name="summary.txt",
                    mime="text/plain"
                )
            
            with col2:
                import csv
                import io
                csv_buffer = io.StringIO()
                csv_writer = csv.writer(csv_buffer)
                csv_writer.writerow(["Type", "Word Count", "Content"])
                csv_writer.writerow(["Transcript", transcript_words, transcript])
                csv_writer.writerow(["Summary", summary_words, summary])
                csv_content = csv_buffer.getvalue()
                
                st.download_button(
                    label="📊 Download as CSV",
                    data=csv_content,
                    file_name="summary.csv",
                    mime="text/csv"
                )
            
            with col3:
                st.download_button(
                    label="✂️ Download Summary Only",
                    data=summary,
                    file_name="summary_only.txt",
                    mime="text/plain"
                )
            
            # Note about cleanup
            st.info("💡 Audio file will be automatically cleaned up on next processing to save space.")
            
            # Note about cleanup
            st.info("💡 Audio file will be automatically cleaned up on next processing to save space.")
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.error("Please try again with a different YouTube URL or check your internet connection.")

