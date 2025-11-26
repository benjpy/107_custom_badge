import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import os
import urllib.parse

# Page Config
st.set_page_config(
    page_title="SOSV Robotics Matchup - Personalize Your Card (beta)",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS for Green Download Button
st.markdown("""
    <style>
    /* Target the download button container */
    div[data-testid="stDownloadButton"] button {
        background-color: #4CAF50 !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
        padding: 0.5rem 1rem !important;
    }
    div[data-testid="stDownloadButton"] button:hover {
        background-color: #45a049 !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# Constants
BASE_IMAGE_PATH = 'card-share.png'
DEFAULT_SHARE_TEXT = """Looking forward to meeting #robotics #investors at the @SOSV Robotics Matchup on Dec 1-5. It's 100% virtual and free > https://sosv.com/sosv-matchups/"""

def process_image(photo_file):
    try:
        base_img = Image.open(BASE_IMAGE_PATH).convert("RGBA")
    except FileNotFoundError:
        st.error("Base image not found on server.")
        return None

    # Process Uploaded Photo (Bottom-Left)
    if photo_file:
        try:
            photo = Image.open(photo_file).convert("RGBA")
            # Target size for bottom-left quadrant
            target_width = 308
            target_height = 309
            
            # Resize/Crop logic
            photo_ratio = photo.width / photo.height
            target_ratio = target_width / target_height
            
            if photo_ratio > target_ratio:
                new_height = target_height
                new_width = int(new_height * photo_ratio)
            else:
                new_width = target_width
                new_height = int(new_width / photo_ratio)
                
            photo = photo.resize((new_width, new_height), Image.LANCZOS)
            
            # Center crop
            left = (new_width - target_width) / 2
            top = (new_height - target_height) / 2
            right = (new_width + target_width) / 2
            bottom = (new_height + target_height) / 2
            
            photo = photo.crop((left, top, right, bottom))
            
            # Paste into bottom-left (0, 309)
            base_img.paste(photo, (0, 309))
            
        except Exception as e:
            st.error(f"Error processing uploaded image: {e}")
            return None

    return base_img

# UI Layout
st.title("SOSV Robotics Matchup - Personalize Your Card (beta)")
st.markdown("Personalize your robotics event card to share with your network.")

col1, col2 = st.columns([1, 1])

# Initialize session state
if 'generated_image' not in st.session_state:
    # Load default image initially
    try:
        st.session_state.generated_image = Image.open(BASE_IMAGE_PATH).convert("RGBA")
    except:
        st.session_state.generated_image = None

with col1:
    st.subheader("Customize")
    uploaded_file = st.file_uploader("Upload your photo, logo or product", type=['png', 'jpg', 'jpeg'])
    
    generate_btn = st.button("Generate Card", type="primary")

    if generate_btn:
        if uploaded_file:
            with st.spinner("Generating..."):
                img = process_image(uploaded_file)
                st.session_state.generated_image = img
        else:
            st.warning("Please upload a photo to customize.")

    # Sharing Section (Moved to Left)
    st.divider()
    st.subheader("Share")
    
    if st.session_state.generated_image:
        # Prepare download
        img_byte_arr = io.BytesIO()
        st.session_state.generated_image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        st.download_button(
            label="Download Image",
            data=img_byte_arr,
            file_name="my-robotics-card.png",
            mime="image/png",
            use_container_width=True
        )
        
        st.warning("⚠️ **Important**: You must **download** the image above and **upload it manually** to your post. Social platforms do not allow automatic image attachment.")
        
        st.markdown("### Post Text")
        share_text = st.text_area("Edit your message here:", value=DEFAULT_SHARE_TEXT, height=150)
        
        st.caption("Copy this text for your post:")
        st.code(share_text, language="text")
        
        col_share_1, col_share_2 = st.columns(2)
        
        with col_share_1:
            # LinkedIn
            st.link_button("Go to LinkedIn", "https://www.linkedin.com/feed/", use_container_width=True)
            
        with col_share_2:
            # X (Twitter)
            encoded_text = urllib.parse.quote(share_text)
            x_url = f"https://twitter.com/intent/tweet?text={encoded_text}"
            st.link_button("Share on X", x_url, use_container_width=True)

with col2:
    st.subheader("Preview")
    if st.session_state.generated_image:
        st.image(st.session_state.generated_image, caption="Your Card", use_container_width=True)
    else:
        st.error("Base image not found.")
