import streamlit as st

import json
import time
from mutagen.mp3 import MP3

# Initialize pygame mixer


# Detect if running on Streamlit Cloud
import os

IS_DEPLOYED = "STREAMLIT_SERVER_PORT" in os.environ

if not IS_DEPLOYED:
    import pygame
    try:
        pygame.mixer.init()
    except Exception as e:
        st.error(f"Error initializing pygame mixer: {e}")
else:
    pygame = None



st.set_page_config(page_title="Streamify+", layout="wide", page_icon="🎵")

mp3_folder = "music"
album_folder = "album_art"

# Load metadata and playlists
metadata = json.load(open("metadata.json"))
playlists = json.load(open("playlists/playlists.json"))

# Add All Songs playlist dynamically
all_songs = []
for songs in playlists.values():
    all_songs.extend(songs)
playlists = {"All Songs": list(dict.fromkeys(all_songs))} | playlists  # All Songs on top

# Sidebar playlist selection
st.sidebar.markdown("""
    <h1 style='text-align: center; color: #1DB954; margin-bottom: 30px;'>
        <span style='color: #1DB954;'>🎵</span> Streamify+
    </h1>
""", unsafe_allow_html=True)

# Custom selectbox styling
st.sidebar.markdown("""
    <style>
        .stSelectbox > div > div {
            background-color: #282828 !important;
            color: white !important;
        }
        .stSelectbox > label {
            color: white !important;
            font-weight: bold;
        }
        .stSelectbox option {
            background-color: #282828 !important;
            color: white !important;
        }
    </style>
""", unsafe_allow_html=True)

playlist_name = st.sidebar.selectbox(
    "Choose a Playlist", 
    list(playlists.keys()),
    key="playlist_selector"
)
music_files = playlists[playlist_name]

# <-- FIX: Ensure song_index is valid for current playlist -->
if "song_index" not in st.session_state:
    st.session_state.song_index = 0
else:
    if st.session_state.song_index >= len(music_files):
        st.session_state.song_index = 0

# Session state setup
if "song_index" not in st.session_state:
    st.session_state.song_index = 0
if "is_playing" not in st.session_state:
    st.session_state.is_playing = False
if "start_time" not in st.session_state:
    st.session_state.start_time = 0
if "last_played" not in st.session_state:
    st.session_state.last_played = None
if "volume" not in st.session_state:
    st.session_state.volume = 0.7
    pygame.mixer.music.set_volume(st.session_state.volume)
if "force_update" not in st.session_state:
    st.session_state.force_update = False

# Get current song info
def get_current_song():
    current_song = music_files[st.session_state.song_index]
    song_path = os.path.join(mp3_folder, current_song)
    meta = metadata.get(current_song, {})
    title = meta.get("title", current_song)
    movie = meta.get("movie", "Unknown Movie")
    singer = meta.get("singer", "Unknown Singer")
    try:
        audio = MP3(song_path)
        duration = int(audio.info.length)
    except Exception:
        duration = 0
    return current_song, song_path, title, movie, singer, duration

# Controls
def play_song():
    current_song, song_path, _, _, _, _ = get_current_song()
    
    if not IS_DEPLOYED and pygame:
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play()
        pygame.mixer.music.set_volume(st.session_state.get("volume", 0.5))
    else:
        # Use streamlit's audio widget
        with open(song_path, "rb") as f:
            audio_bytes = f.read()
        st.audio(audio_bytes, format="audio/mp3", start_time=0)

    st.session_state.last_played = current_song
    st.session_state.start_time = time.time()
    st.session_state.is_playing = True
    st.session_state.force_update = False

def stop_song():
    if not IS_DEPLOYED and pygame:
        pygame.mixer.music.stop()
    st.session_state.is_playing = False
    st.session_state.start_time = 0

def change_song(delta):
    stop_song()
    st.session_state.song_index = (st.session_state.song_index + delta) % len(music_files)
    st.session_state.last_played = None
    st.session_state.is_playing = False
    st.session_state.start_time = 0
    st.session_state.force_update = True
    play_song()

def set_volume(volume):
    st.session_state.volume = volume
    if not IS_DEPLOYED and pygame:
        pygame.mixer.music.set_volume(volume)

st.markdown("""
    <style>
    /* Define variables for both themes */
    .light-theme {
        --primary: #1DB954;
        --background: #FFFFFF;
        --card: #F4F4F4;
        --text: #000000;
        --text-secondary: #555555;
    }

    .dark-theme {
        --primary: #1DB954;
        --background: #121212;
        --card: #181818;
        --text: #FFFFFF;
        --text-secondary: #B3B3B3;
    }

    /* Apply theme variables to body (default to light theme) */
    body {
        background-color: var(--background);
        color: var(--text);
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #000000 !important;
        border-right: 1px solid #282828;
    }

    /* Main container */
    .main {
        background: var(--background);
        padding: 2rem;
    }

    /* Default style (e.g., dark theme or fallback) */
    .now-playing-card {
        background-color: var(--card);
        border-radius: 12px;
        padding: 2rem;
        box-shadow: 0 8px 24px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }

    /* Override for light theme */
    .light-theme .now-playing-card {
        background-color: black;
    }


    /* Song info */
    .song-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: var(--text) !important;
    }

    .song-artist {
        font-size: 1.2rem;
        color: var(--text-secondary) !important;
    }

    .song-movie {
        font-size: 1.5rem;
        color: var(--text-secondary) !important;
    }

    /* Player buttons */
    .control-button {
        background-color: transparent !important;
        color: var(--text) !important;
        border: none !important;
        font-size: 2rem !important;
        padding: 0.5rem !important;
        margin: 0 0.5rem !important;
    }

    .play-button {
        background-color: var(--primary) !important;
        border-radius: 50% !important;
        width: 60px !important;
        height: 60px !important;
        font-size: 1.5rem !important;
    }

    /* Progress bar */
    .progress-container {
        width: 100%;
        height: 6px;
        background-color: #ccc;
        border-radius: 3px;
        margin: 2rem 0;
        cursor: pointer;
    }

    .progress-bar {
        height: 100%;
        background-color: var(--primary);
        border-radius: 3px;
        width: 0%;
    }

    /* Time display */
    .time-display {
        display: flex;
        justify-content: space-between;
        color: var(--text-secondary);
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }

    /* Download button */
    .download-btn {
        background-color: transparent !important;
        color: var(--primary) !important;
        border: 1px solid var(--primary) !important;
        border-radius: 20px !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 600 !important;
        margin-top: 1rem !important;
    }

    .download-btn:hover {
        background-color: rgba(29, 185, 84, 0.1) !important;
    }

    /* Volume */
    .volume-slider {
        width: 100px !important;
        margin-left: 1rem !important;
    }

    /* Playlist */
    .playlist-header {
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        color: var(--text);
    }

    .playlist-item {
        padding: 1rem;
        margin-bottom: 0.5rem;
        border-radius: 4px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: background-color 0.2s;
        color: var(--text);
    }

    .playlist-item:hover {
        background-color: #282828;
        color: #FFFFFF;
    }

    .playlist-item:hover div {
        color: #FFFFFF;
    }

    .current-song {
        background-color: rgba(29, 185, 84, 0.1);
        border-left: 4px solid #1DB954;
    }

    /* Header emoji */
    .header-emoji {
        color: #1DB954 !important;
        text-shadow: 0 0 10px rgba(29, 185, 84, 0.5);
    }

    /* Select box dropdown styling */
    .stSelectbox div[data-baseweb="select"] div {
        color: white !important;
        background-color: #282828 !important;
    }

    .stSelectbox div[data-baseweb="popover"] div {
        color: white !important;
        background-color: #282828 !important;
    }

    .stSelectbox div[data-baseweb="popover"] div:hover {
        background-color: #383838 !important;
    }
    </style>
    """, unsafe_allow_html=True)



current_song, song_path, title, movie, singer, duration = get_current_song()

# Main layout
st.markdown("""
    <h1 style='text-align:center; color: #1DB954;'>
        <span class='header-emoji'>🎵</span> Streamify+ Music Player
    </h1>
    </h1>
    <p style='text-align:center; color: #AAAAAA; font-size: 20px; margin-top: -10px;'>
        Created by <strong>Kaustav Roy Chowdhury</strong> with ❤️
    </p>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("<div class='now-playing-card'>", unsafe_allow_html=True)
    
    art_path = os.path.join(album_folder, current_song.replace(".mp3", ".jpg"))
    if os.path.exists(art_path):
        st.image(art_path, use_container_width=True)  # Changed from use_column_width
    else:
        st.markdown("""
            <div style='background-color: #282828; width: 100%; aspect-ratio: 1; 
                      border-radius: 12px; display: flex; align-items: center; 
                      justify-content: center;'>
                <span style='font-size: 3rem; color: #535353;'>🎵</span>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='now-playing-card'>", unsafe_allow_html=True)
    
    st.markdown(f"<div class='song-title'>{title}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='song-artist'>{singer}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='song-movie'>From: {movie}</div>", unsafe_allow_html=True)
    
    # Progress bar
    elapsed = int(time.time() - st.session_state.start_time) if st.session_state.is_playing else 0
    progress_percent = (elapsed / duration * 100) if duration > 0 else 0
    
    st.markdown(f"""
        <div class='progress-container'>
            <div class='progress-bar' style='width: {progress_percent}%'></div>
        </div>
        <div class='time-display'>
            <span>{time.strftime('%M:%S', time.gmtime(elapsed))}</span>
            <span>{time.strftime('%M:%S', time.gmtime(duration))}</span>
        </div>
    """, unsafe_allow_html=True)
    
    # Player controls
    control_cols = st.columns([1, 1, 2, 1, 1])

    with control_cols[0]:
        if st.button("⏮", key="prev", help="Previous"):
            change_song(-1)
            st.rerun()

    with control_cols[1]:
        if st.button("⏹", key="stop", help="Stop"):
            stop_song()
            st.rerun()

    with control_cols[2]:
        if st.button("▶️", key="play", help="Play"):
            play_song()
            st.rerun()

    with control_cols[3]:
        if st.button("⏭", key="next", help="Next"):
            change_song(1)
            st.rerun()
        
    # Download button
    with open(song_path, "rb") as f:
        st.download_button(
            "Download MP3", 
            f, 
            file_name=current_song, 
            mime="audio/mpeg", 
            use_container_width=True
        )
    
    st.markdown("</div>", unsafe_allow_html=True)

# Current playlist
st.markdown(f"<div class='playlist-header'>Songs in {playlist_name}</div>", unsafe_allow_html=True)

for i, song in enumerate(music_files):
    meta = metadata.get(song, {})
    song_title = meta.get("title", song)
    song_singer = meta.get("singer", "Unknown Singer")
    
    # Create a container for each song
    container = st.container()
    
    # Highlight currently playing song
    if i == st.session_state.song_index:
        container.markdown(
            f"""
            <div class='playlist-item current-song'>
                <div>
                    <div style='font-weight: 500;'>{song_title}</div>
                    <div style='font-size: 0.9rem; color: var(--text-secondary);'>{song_singer}</div>
                </div>
                <div>▶️</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        container.markdown(
            f"""
            <div class='playlist-item'>
                <div>
                    <div style='font-weight: 500;'>{song_title}</div>
                    <div style='font-size: 0.9rem; color: var(--text-secondary);'>{song_singer}</div>
                </div>
                <div>▶️</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Add click functionality
    if container.button("Play", key=f"play_{i}", help=f"Play {song_title}"):
        st.session_state.song_index = i
        st.session_state.last_played = None
        st.session_state.force_update = True
        play_song()
        st.rerun()

# Auto-play if nothing playing
# Auto-play only if app just started or user requested it
if (
    not pygame.mixer.music.get_busy() and 
    not st.session_state.is_playing and 
    st.session_state.last_played is None
):
    play_song()
