
import streamlit as st
from backend import process_sheet_music
import tempfile
import os

st.title("🎼 HARMOSEE 🎼")
st.title("sheet music to piano video converter")

uploaded_image = st.file_uploader(
    "Upload your sheet music image",
    type=["png", "jpg", "jpeg", "bmp", "tiff"],
    help="Supported formats: PNG, JPG, JPEG, BMP, TIFF"
)

if uploaded_image is not None:
    st.image(uploaded_image, caption="Uploaded Image", use_container_width=True)

    if st.button("Convert to Video"):
        image_bytes = uploaded_image.getvalue()

        with st.spinner("Processing... 🎶"):
            try:
                # Save uploaded image temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_img:
                    temp_img.write(image_bytes)
                    temp_img_path = temp_img.name

                # Run backend processing
                result = process_sheet_music(temp_img_path)
                video_path = result["video"]

                if not os.path.exists(video_path):
                    st.error("❌ Video file was not created.")
                else:
                    st.success("✅ Conversion complete!")

                    # Display video directly from path
                    st.video(video_path)

                    # Provide download button
                    with open(video_path, "rb") as video_file:
                        video_bytes = video_file.read()
                        st.download_button(
                            label="⬇ Download Your Piano Video",
                            data=video_bytes,
                            file_name="piano_output.mp4",
                            mime="video/mp4"
                        )

            except Exception as e:
                st.error(f"❌ An error occurred: {e}")
            finally:
                # Only delete the uploaded image, not the video
                if 'temp_img_path' in locals() and os.path.exists(temp_img_path):
                    os.remove(temp_img_path)
                # ⚠️ Do NOT delete video_path here — let Streamlit finish using it

else:
    st.info("Please upload a sheet music image to get started.")