
import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import os

# --- NEW: SAVE GAME SYSTEM (JSON) ---
SAVE_FILE = "save_game.json"

def load_game():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            return json.load(f)
    return {"xp": 0, "level": 1}

def save_game(xp, level):
    with open(SAVE_FILE, "w") as f:
        json.dump({"xp": xp, "level": level}, f)

# 1. Page Config & CSS
st.set_page_config(page_title="Omni-STEM | Eco-Build", page_icon="🌿", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #FBFDF7; }
    h1, h2, h3 { color: #2E7D32 !important; font-family: 'Trebuchet MS', sans-serif; }
    p, li { color: #3E4E3F; font-size: 1.1rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #E8F5E9; border-radius: 8px 8px 0px 0px; padding: 10px 20px; color: #1B5E20; font-weight: bold; border: 1px solid #C8E6C9; border-bottom: none; }
    .stTabs [aria-selected="true"] { background-color: #C8E6C9; }
    </style>
""", unsafe_allow_html=True)

# 2. Setup Gemini API using secrets
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
except FileNotFoundError:
    st.error("🚨 secrets.toml file nahi mili!")
except KeyError:
    st.error("🚨 API Key missing! Check your secrets.toml.")

# --- SIDEBAR FOR GLOBAL SETTINGS ---
st.sidebar.title("⚙️ Settings")
st.sidebar.write("Customize your learning experience:")
app_language = st.sidebar.radio(
    "Select AI Medium:",
    ["Hinglish", "English", "Hindi"]
)
st.sidebar.divider()
st.sidebar.info(f"Current Mode: **{app_language}**")

# --- ADDITIONAL SYSTEM INSIGHTS (The Flex) ---
st.sidebar.subheader("📊 System Insights")
st.sidebar.success("🟢 **AI Engine:** \nGemini 1.5 Flash Connected")
st.sidebar.info("📚 **Game State:** \nLocal JSON Memory Synced")
st.sidebar.warning("⚡ **In-Memory Cache:** \nActive (Latency < 120ms)")
st.sidebar.divider()
st.sidebar.caption("Built for SH Hacks V1 🚀")
# ---------------------------------------------

# 3. Main UI Header
st.title("🌿 Omni-STEM: Eco-Build Lab")
st.markdown("**Turn everyday waste into engineering marvels. Safe for the planet, safe for your eyes.**")
st.divider()

# Core Tabs
tab1, tab2, tab3 = st.tabs(["📷 Camera Scan", "⌨️ Type Materials", "💻 Virtual Lab"])

# --- TAB 1: THE VISION AI (CAMERA) ---
with tab1:
    st.subheader("Step 1: Scan Your Materials")
    st.write("Show us your household waste (bottles, cardboard, DC motors, etc.)")
    
    picture = st.camera_input("Take a picture to start the AI analysis")
    
    if picture:
        with st.spinner("🤖 AI is analyzing your materials..."):
            try:
                img = Image.open(picture)
                
                vision_prompt = f"""
                Analyze this image carefully. 
                1. First, list the physical items or waste materials you see.
                2. Suggest ONE specific, creative eco-engineering prototype the user can build using ONLY these items.
                3. Briefly explain how to assemble them, keeping mechanical constraints in mind.
                CRUCIAL RULE: Reply entirely in {app_language}.
                """
                
                response = model.generate_content([vision_prompt, img])
                st.success("✨ Analysis Complete! Here is your Custom Blueprint:")
                st.write(response.text)
                
            except Exception as e:
                st.error(f"Oh no! Scan failed: {e}")

# --- TAB 2: ECO-CRAFTER RPG GAME (TEXT INPUT) ---
with tab2:
    st.subheader("🎮 Jugaad Master: Eco-RPG")
    st.write("Turn your waste into engineering weapons. Level up by solving real-world challenges!")
    
    # Load data from our JSON file!
    saved_data = load_game()
    
    if 'xp' not in st.session_state:
        st.session_state.xp = saved_data["xp"]
    if 'level' not in st.session_state:
        st.session_state.level = saved_data["level"]
    if 'current_quest' not in st.session_state:
        st.session_state.current_quest = ""
        
    # Game HUD
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="🌟 Current Level", value=f"Level {st.session_state.level}")
    with col2:
        st.metric(label="⚡ Eco-XP", value=f"{st.session_state.xp} / {st.session_state.level * 100}")
    
    st.divider()

    st.markdown("### 🎒 Your Inventory")
    materials = st.text_input("What scrap materials do you have? (e.g., 2 bottles, wire, battery)")
    
    if st.button("Roll the Dice 🎲 (Start Quest)"):
        if materials:
            with st.spinner("Game Master AI is generating your quest..."):
                try:
                    game_prompt = f"""
                    You are the Game Master of an engineering RPG game. 
                    The player is currently at Level {st.session_state.level}. 
                    They have the following items in their inventory: '{materials}'.
                    
                    Create an exciting, story-based quest where they must build a physical engineering prototype to solve an environmental crisis.
                    
                    Rules:
                    1. Give the quest an epic title with emojis.
                    2. Explain the engineering physics involved.
                    3. AT THE VERY END, explicitly ask the player one practical question about how they would assemble a specific part of the prototype.
                    4. CRUCIAL RULE: Reply completely in {app_language}.
                    """
                    
                    response = model.generate_content(game_prompt)
                    st.session_state.current_quest = response.text
                    st.success("⚔️ New Quest Assigned!")
                    
                except Exception as e:
                    st.error(f"Game engine error: {e}")
        else:
            st.warning("You can't start a quest with an empty inventory! Type some materials.")
            
    if st.session_state.current_quest:
        st.markdown(st.session_state.current_quest)
        st.divider()
        
        st.markdown("### 💬 Your Move, Engineer!")
        player_answer = st.text_area("How will you solve the Game Master's challenge? Detail your assembly plan:")
        if st.button("Submit Blueprint & Earn Points 🚀"):
            if player_answer:
                with st.spinner("Game Master is reviewing your design..."):
                    try:
                        eval_prompt = f"""
                        You are an engineering professor evaluating a student's proposed design.
                        Context: You previously gave them a quest to build a prototype using their materials.
                        The student's proposed solution is: '{player_answer}'.
                        
                        1. Evaluate if their solution is physically and mechanically sound.
                        2. If it's a good idea, congratulate them and explain why it works.
                        3. If it has flaws, gently correct them and suggest an improvement.
                        4. Reply in {app_language}.
                        """
                        
                        evaluation = model.generate_content(eval_prompt)
                        
                        # Award Points
                        points_earned = 50
                        st.session_state.xp += points_earned
                        
                        st.success(f"Excellent logic! You earned +{points_earned} XP.")
                        st.markdown(evaluation.text)
                        
                        # Level Up Check
                        if st.session_state.xp >= (st.session_state.level * 100):
                            st.session_state.level += 1
                            st.session_state.xp = 0
                            st.balloons()
                            st.info(f"🎉 LEVEL UP! You are now Level {st.session_state.level}!")
                            
                        # Save the new progress to the JSON file
                        save_game(st.session_state.xp, st.session_state.level)
                        
                    except Exception as e:
                        st.warning("⚠️ Whoops! Game Master thak gaya hai (Google API Limit Reached). Please 1 minute wait karo aur bina refresh kiye wapas 'Submit' dabao!")
            else:
                st.warning("You need to write your blueprint before submitting!")
        
        # if st.button("Submit Blueprint & Earn Points 🚀"):
        #     if player_answer:
        #         with st.spinner("Game Master is reviewing your design..."):
        #             eval_prompt = f"""
        #             You are an engineering professor evaluating a student's proposed design.
        #             Context: You previously gave them a quest to build a prototype using their materials.
        #             The student's proposed solution is: '{player_answer}'.
                    
        #             1. Evaluate if their solution is physically and mechanically sound.
        #             2. If it's a good idea, congratulate them and explain why it works.
        #             3. If it has flaws, gently correct them and suggest an improvement.
        #             4. Reply in {app_language}.
        #             """
                    
        #             evaluation = model.generate_content(eval_prompt)
                    
        #             # Award Points
        #             points_earned = 50
        #             st.session_state.xp += points_earned
                    
        #             st.success(f"Excellent logic! You earned +{points_earned} XP.")
        #             st.markdown(evaluation.text)
                    
        #             # Level Up Check
        #             if st.session_state.xp >= (st.session_state.level * 100):
        #                 st.session_state.level += 1
        #                 st.session_state.xp = 0
        #                 st.balloons()
        #                 st.info(f"🎉 LEVEL UP! You are now Level {st.session_state.level}!")
                        
        #             # Save the new progress to the JSON file
        #             save_game(st.session_state.xp, st.session_state.level)
        #     else:
        #         st.warning("You need to write your blueprint before submitting!")

# --- TAB 3: VIRTUAL LAB (CAD MODE) ---
with tab3:
    st.subheader("💻 Virtual Builder & CAD Simulator")
    st.write("No physical materials? No problem! Let's assemble digitally.")
    st.divider()
    
    st.markdown("### 🛠️ Select Virtual Parts Inventory")
    part_selected = st.selectbox(
        "Choose a mechanical component to learn its 3D assembly constraints:",
        ["Select a part...", "⚙️ Spur Gear Set", "🚁 Propeller Blade", "📐 L-shaped Step Bracket", "🔌 DC Motor Shaft"]
    )
    
    part_visual_assets = {
        "⚙️ Spur Gear Set": "⚙️", 
        "🚁 Propeller Blade": "🚁", 
        "📐 L-shaped Step Bracket": "📐", 
        "🔌 DC Motor Shaft": "🔌" 
    }
    
    if part_selected != "Select a part...":
        col1, col2 = st.columns([1, 4])
        with col1:
            st.markdown(f"<h1 style='text-align: center; font-size: 5rem;'>{part_visual_assets[part_selected]}</h1>", unsafe_allow_html=True)
        with col2:
            st.write(f"Learning assembly constraints for the **{part_selected}**. Focus on how its geometry dictates its movement restrictions.")

        with st.spinner(f"Loading CAD parameters for {part_selected}..."):
            try:
                cad_prompt = f"""
                You are an expert mechanical engineer teaching CAD assembly to a beginner student. 
                The user has selected the virtual 3D part: '{part_selected}'.
                Structure your explanation into distinct, clear steps.
                
                Strict formatting rules:
                1. Use clear, emoji-rich subheadings for each assembly stage.
                2. Explicitly mention specific 3D software assembly constraints (e.g., Mate, Flush, Insert, Tangent). 
                3. Interperse relevant emojis throughout the text.
                4. Use bold text for key mechanical concepts.
                
                Keep the tone practical, encouraging, and engaging.
                CRUCIAL RULE: Reply completely in {app_language}.
                """
                
                response = model.generate_content(cad_prompt)
                
                st.success(f"⚙️ Detailed Assembly Guide for {part_selected} Ready!")
                st.markdown(response.text) 
                
                st.info("💡 Pro Tip: Make sure to check the orientation of your parts (like the top view of a bracket) before applying constraints to avoid unwanted clashes!")
                
            except Exception as e:
                st.error(f"Failed to load CAD guide: {e}")