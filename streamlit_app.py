# -*- coding: utf-8 -*-

import imghdr
import io
import json
import os
import tempfile
import time
import uuid
import zipfile
from pathlib import Path

import streamlit as st
from PIL import Image, ImageSequence
from dotenv import load_dotenv

# from gotipy import Gotify
from loguru import logger
from rembg.bg import remove


def remove_bg(input_data, path):
    result = remove(input_data)
    img = Image.open(io.BytesIO(result)).convert("RGBA")
    if Path(path).suffix != ".png":
        img.LOAD_TRUNCATED_IMAGES = True
    return img


def gif2frames(input_file, skip_every=1):
    im = Image.open(input_file)
    include_frames = range(0, len(list(ImageSequence.Iterator(im))), skip_every)

    frames = []

    for n, frame in enumerate(ImageSequence.Iterator(im)):
        if n not in include_frames:
            continue
        frame.copy()
        bytes_obj = io.BytesIO()
        frame.save(bytes_obj, format="PNG")
        frames.append((n, bytes_obj.getvalue()))
    return frames


def main():
    if st.sidebar.button("CLEAR"):
        st.session_state["key"] = K
        st.experimental_rerun()
    st.sidebar.markdown("---")

    accept_multiple_files = True
    accepted_type = ["png", "jpg", "jpeg", "gif"]

    uploaded_files = st.sidebar.file_uploader(
        f"Choose one or multiple files (max: {MAX_FILES})",
        type=accepted_type,
        accept_multiple_files=accept_multiple_files,
        key=st.session_state["key"],
    )

    if len(uploaded_files) > MAX_FILES != -1:
        st.warning(
            f"Maximum number of files reached! Only the first {MAX_FILES} "
            "will be processed."
        )
        uploaded_files = uploaded_files[:MAX_FILES]

    uploaded_files = [x for x in uploaded_files if x]

    if uploaded_files:
        logger.info(f"Uploaded the following files: {uploaded_files}")

        progress_bar = st.empty()
        down_btn = st.empty()
        cols = st.empty()
        col1, col2 = cols.columns(2)
        imgs_bytes = []
        frames = []

        IS_GIF = False
        if any(Path(x.name).suffix.lower() == ".gif" for x in uploaded_files):
            IS_GIF = True
            if len(uploaded_files) > 1:
                st.error(
                    f"The maximum number of allowed uploads when processing a "
                    "GIF is one file!"
                )
                return

            dur_text = "Duration (in milliseconds) of each frame:"
            duration = st.sidebar.slider(dur_text, 0, 1000, 100, 10)
            frames = gif2frames(uploaded_files[0])

        for uploaded_file in uploaded_files:
            bytes_data = uploaded_file.getvalue()

            if imghdr.what(file="", h=bytes_data) not in accepted_type:
                st.error(f"`{uploaded_file.name}` is not a valid image!")
                continue

            if "btn" not in st.session_state:
                st.session_state.my_button = True
                imgs_bytes.append((uploaded_file, bytes_data))

        col1.image([x[1] for x in imgs_bytes])

        nobg_imgs = []
        if st.sidebar.button("Remove background"):
            pb = progress_bar.progress(0)

            if frames:
                imgs_bytes = frames

            with st.spinner("Wait for it..."):
                for n, (uploaded_file, bytes_data) in enumerate(imgs_bytes, start=1):
                    if isinstance(uploaded_file, int):
                        p = Path(str(uploaded_file) + ".png")
                    else:
                        p = Path(uploaded_file.name)

                    img = remove_bg(bytes_data, p)
                    with io.BytesIO() as f:
                        img.save(f, format="PNG", quality=100, subsampling=0)
                        data = f.getvalue()
                    nobg_imgs.append((img, p, data))

                    cur_progress = int(100 / len(imgs_bytes))
                    pb.progress(cur_progress * n)
                time.sleep(1)
                progress_bar.empty()
                pb.success("Complete!")

                nobg_images = [x[0] for x in nobg_imgs]

                if IS_GIF:
                    col2.markdown(
                        "🧪 *Use [ezgif.com](https://ezgif.com/) to create "
                        "the GIF file and edit individual frames.*"
                    )
                col2.image(nobg_images)

            if len(nobg_imgs) > 1:
                with io.BytesIO() as tmp_zip:
                    with zipfile.ZipFile(tmp_zip, "w") as z:
                        for img, p, data in nobg_imgs:
                            with tempfile.NamedTemporaryFile() as fp:
                                img.save(fp.name, format="PNG")
                                z.write(
                                    fp.name,
                                    arcname=p.name,
                                    compress_type=zipfile.ZIP_DEFLATED,
                                )
                    zip_data = tmp_zip.getvalue()

                if IS_GIF:
                    frames_literal = "(individual frames)"
                else:
                    frames_literal = ""

                down_btn.download_button(
                    label=f"Download all results {frames_literal}",
                    data=zip_data,
                    file_name=f"results_{int(time.time())}.zip",
                    mime="application/zip",
                    key="btn",
                )
            else:
                try:
                    out = nobg_imgs[0]
                    down_btn.download_button(
                        label="Download result",
                        data=out[-1],
                        file_name=f"{out[1].stem}_nobg.png",
                        mime="image/png",
                        key="btn",
                    )
                except IndexError:
                    st.error("No more images to process!")
                finally:
                    st.session_state["key"] = K


if __name__ == "__main__":
    st.set_page_config(
        page_title="Remove Background", page_icon="✂️", initial_sidebar_state="expanded"
    )
    st.markdown(
        "<style> footer {visibility: hidden;}"
        "#MainMenu {visibility: hidden;}</style>",
        unsafe_allow_html=True,
    )
    logger.add("logs.log")

    load_dotenv()

    MAX_FILES = 10
    if os.getenv("MAX_FILES"):
        MAX_FILES = int(os.getenv("MAX_FILES"))

    GOTIFY = False
    if os.getenv("GOTIFY_HOST_ADDRESS") and os.getenv("GOTIFY_APP_TOKEN"):
        GOTIFY = True

    K = str(uuid.uuid4())
    if "key" not in st.session_state:
        st.session_state["key"] = K

    main()
