import streamlit as st
import asyncio
import edge_tts
import os
from pydub import AudioSegment
import re

# पेज कॉन्फ़िगरेशन
st.set_page_config(page_title="Hindi Podcast Generator", page_icon="🎙️")

st.title("🎙️ AI Hindi Podcast Generator")
st.subheader("Script डालिये और मल्टी-कैरेक्टर पॉडकास्ट बनाइये")

# हिंदी आवाज़ों की लिस्ट
VOICES = {
    "Swara (Female)": "hi-IN-SwaraNeural",
    "Madhur (Male)": "hi-IN-MadhurNeural",
    "Google (English-Female)": "en-US-EmmaNeural",
    "Google (English-Male)": "en-US-BrianNeural"
}

# ऑडियो जनरेट करने का फंक्शन
async def generate_audio_segment(text, voice, filename):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(filename)

# मुख्य UI
script_input = st.text_area(
    "अपनी स्क्रिप्ट यहाँ लिखें (Format: Name: Dialogue)",
    placeholder="Rohan: नमस्ते अंजलि, कैसी हो?\nAnjali: मैं ठीक हूँ रोहन, तुम बताओ।",
    height=300
)

if script_input:
    # कैरेक्टर्स को पहचानना (Regex का उपयोग करके)
    lines = script_input.strip().split('\n')
    characters = set()
    parsed_script = []

    for line in lines:
        if ":" in line:
            name, text = line.split(":", 1)
            name = name.strip()
            text = text.strip()
            characters.add(name)
            parsed_script.append((name, text))

    if characters:
        st.write("### कैरेक्टर्स के लिए आवाज़ चुनें:")
        char_voice_map = {}
        cols = st.columns(len(characters))
        
        for i, char in enumerate(characters):
            with cols[i]:
                char_voice_map[char] = st.selectbox(f"{char}", list(VOICES.keys()), key=char)

        if st.button("पॉडकास्ट जनरेट करें"):
            with st.spinner("आवाज़ तैयार की जा रही है... कृपया इंतज़ार करें।"):
                combined_audio = AudioSegment.empty()
                temp_files = []

                try:
                    for i, (name, text) in enumerate(parsed_script):
                        voice_key = char_voice_map[name]
                        voice_id = VOICES[voice_key]
                        filename = f"temp_{i}.mp3"
                        
                        # आवाज़ जनरेट करें
                        asyncio.run(generate_audio_segment(text, voice_id, filename))
                        temp_files.append(filename)
                        
                        # ऑडियो को जोड़ें
                        segment = AudioSegment.from_mp3(filename)
                        combined_audio += segment + AudioSegment.silent(duration=500) # थोड़ा गैप

                    # फाइनल फाइल सेव करें
                    final_filename = "podcast_output.mp3"
                    combined_audio.export(final_filename, format="mp3")

                    st.success("✅ पॉडकास्ट तैयार है!")
                    st.audio(final_filename)
                    
                    with open(final_filename, "rb") as f:
                        st.download_button("MP3 डाउनलोड करें", f, file_name="my_podcast.mp3")

                except Exception as e:
                    st.error(f"Error: {e}")
                
                finally:
                    # टेम्परेरी फाइलें डिलीट करें
                    for f in temp_files:
                        if os.path.exists(f):
                            os.remove(f)
    else:
        st.warning("कृपया सही फॉर्मेट में स्क्रिप्ट लिखें (जैसे - नाम: डायलॉग)")

st.markdown("---")
st.caption("Developed for Hindi Podcast Creators | Free & Open Source")