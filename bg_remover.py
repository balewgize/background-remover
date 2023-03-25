import io
import tempfile
import time
import uuid
import zipfile
from pathlib import Path

import streamlit as st
from PIL import Image

# from loguru import logger
from rembg import remove


MAX_FILES = 5  # number of images to be processed once
MULTIPLE_IMAGES_ALLOWED = True
ALLOWED_TYPES = ["png", "jpg", "jpeg"]


def remove_bg(input_data, path):
    """Remove background from an image using rembg."""
    result = remove(input_data)
    img = Image.open(io.BytesIO(result)).convert("RGBA")
    if Path(path).suffix != ".png":
        img.LOAD_TRUNCATED_IMAGES = True
    return img


def build_ui():
    """Show UI of the app with file upload form"""
    st.markdown("### Image Backgroud Remover")
    st.markdown("Remove background from images using pre-trained ML model.")
    st.markdown("\n")

    if st.sidebar.button("CLEAR"):
        st.session_state["key"] = session_id
        st.experimental_rerun()

    st.sidebar.markdown("---")

    uploaded_files = st.sidebar.file_uploader(
        f"Choose one or multiple images (max: {MAX_FILES})",
        type=ALLOWED_TYPES,
        accept_multiple_files=MULTIPLE_IMAGES_ALLOWED,
        key=st.session_state["key"],
    )
    footer = """
    <div style="position: fixed; bottom: 0;">
    <p>Developed with ❤ by <a href="https://github.com/balewgize" target="_blank">@balewgize</a></p>
    </div>"""
    st.sidebar.markdown(footer, unsafe_allow_html=True)

    return uploaded_files


def get_image_bytes(uploaded_files):
    """Return bytes data for each uploaded file."""
    img_bytes = []
    for uploaded_file in uploaded_files:
        bytes_data = uploaded_file.getvalue()
        if "btn" not in st.session_state:
            # st.session_state.my_button = True
            img_bytes.append((uploaded_file, bytes_data))

    return img_bytes


def main():
    uploaded_files = build_ui()

    if len(uploaded_files) > MAX_FILES:
        st.warning(
            f"Maximum number of images reached! Only the first {MAX_FILES} will be processed."
        )
        uploaded_files = uploaded_files[:MAX_FILES]

    # uploaded_files = [img for img in uploaded_files if img]
    if not uploaded_files:
        return

    # logger.info(f"Uploaded the following files: {uploaded_files}")

    progress_bar = st.empty()
    download_btn = st.empty()

    image_row = st.empty()  # row to hold original and result image
    original, result = image_row.columns(2)
    st.text("\n")

    # show original images
    img_bytes = get_image_bytes(uploaded_files)
    for b in img_bytes:
        original.image(b[1], caption="Original")

    if not st.sidebar.button("Remove Background"):
        return

    nobg_images = []  # result images with no background

    progress_text = "Operation in progress. Please wait."
    progress = progress_bar.progress(0, text=progress_text)

    with st.spinner("Processing image..."):
        for i, image_byte in enumerate(img_bytes, start=1):
            uploaded_file, bytes_data = image_byte
            if isinstance(uploaded_file, int):
                img_path = Path(str(uploaded_file) + ".png")
            else:
                img_path = Path(uploaded_file.name)

            img = remove_bg(bytes_data, img_path)
            with io.BytesIO() as f:
                img.save(f, format="PNG", quality=100, subsampling=0)
                data = f.getvalue()

            nobg_images.append((img, img_path, data))

            cur_progress = int(100 / len(img_bytes))
            progress.progress(cur_progress * i)

        time.sleep(1)
        progress_bar.empty()
        progress.success("Complete!")

        # show result image along side original image
        for res in nobg_images:
            result.image(res[0], caption="Result")

    # multiple results will be downloaded as zip file
    if len(nobg_images) > 1:
        with io.BytesIO() as tmp_zip:
            with zipfile.ZipFile(tmp_zip, "w") as z:
                for img, path, data in nobg_images:
                    with tempfile.NamedTemporaryFile() as fp:
                        img.save(fp.name, format="PNG")
                        z.write(
                            fp.name,
                            arcname=path.name,
                            compress_type=zipfile.ZIP_DEFLATED,
                        )
            zip_data = tmp_zip.getvalue()

        download_btn.download_button(
            label=f"Download as ZIP",
            data=zip_data,
            file_name=f"results_{int(time.time())}.zip",
            mime="application/zip",
            key="btn",
        )
    else:
        try:
            output = nobg_images[0]
            download_btn.download_button(
                label="Download Result",
                data=output[-1],
                file_name=f"{output[1].stem}_nobg.png",
                mime="image/png",
                key="btn",
            )
        except IndexError:
            st.error("No more images to process!")
        finally:
            st.session_state["key"] = session_id

    time.sleep(3)
    progress_bar.empty()


if __name__ == "__main__":
    # logger.add("logs.log")

    st.set_page_config(
        page_title="Background Remover",
        page_icon="✂️",
        initial_sidebar_state="expanded",
    )
    st.markdown(
        "<style> footer {visibility: hidden;} #MainMenu {visibility: hidden;}</style>",
        unsafe_allow_html=True,
    )
    session_id = str(uuid.uuid4())
    if "key" not in st.session_state:
        st.session_state["key"] = session_id

    main()
