import os
import streamlit as st
import cv2
from pyzbar import pyzbar
import time

# Get the current directory of the script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the relative path to the video file
# TEMP_VIDEO_PATH = os.path.join(current_dir, "tmp\\parsing.mp4")
TEMP_VIDEO_PATH = "tmp\\parsing.mp4"


def scan_qr(video_path):
    """
    Scans a video file for QR codes and returns a list of decoded QR code data.

    Parameters:
    - video_path (str): The path to the video file to be scanned.

    Returns:
    - qr_codes (list): A list of strings representing the decoded data from the QR codes found in the video.

    """

    cap = cv2.VideoCapture(video_path)
    qr_codes = []
    frame_count = 0
    match_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        frame_count += 1

        if frame_count % st.session_state.frame_rate != 0:
            continue

        if not ret:
            break

        # Convert the frame to grayscale for QR code detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect QR codes in the frame
        barcodes = pyzbar.decode(gray)

        # Process each detected QR code
        for barcode in barcodes:
            # Extract the bounding box coordinates of the QR code
            (x, y, w, h) = barcode.rect

            # Draw a rectangle around the QR code
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            # Extract the data encoded in the QR code
            qr_data = barcode.data.decode("utf-8")

            # Display the QR code data below the bounding box and centerize
            text_width, _ = cv2.getTextSize(qr_data, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[
                0
            ]
            text_x = x + (w - text_width) // 2
            text_y = y + h + 20
            cv2.putText(
                frame,
                qr_data,
                (text_x, text_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 0, 0),
                2,
            )

            # Check if the QR code matches the search code
            if st.session_state.search_code.lower() == qr_data.lower():
                # Centerize the text
                text_width, _ = cv2.getTextSize(
                    qr_data, cv2.FONT_HERSHEY_SIMPLEX, 1, 2
                )[0]
                text_x = x + (w - text_width) // 2
                text_y = y - 10
                cv2.putText(
                    frame,
                    qr_data,
                    (text_x, text_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2,
                )
                match_count += 1

        # Break the loop if 3 matches are found
        if match_count >= 3:
            qr_codes.append(qr_data)
            break

        # Display the frame with QR codes with st.video
        st.session_state.scanning_image.image(frame, channels="BGR")

    # Release the video capture and close the OpenCV windows
    cap.release()

    return qr_codes


def scan_video_files():
    """
    Scans a list of video files for a specific QR code.

    Returns:
        None
    """

    if st.button("Click to scan", type="primary"):
        st.session_state.scanning_text = st.sidebar.empty()
        st.session_state.scanning_image = st.image([], channels="BGR")
        st.session_state.search_code_found = False

        start_time = time.time()
        for video_file in st.session_state.video_files:
            st.session_state.scanning_text.info(f"Scanning file: {video_file.name}...")

            # Save the uploaded video file to a temporary location
            with open(TEMP_VIDEO_PATH, "wb") as f:
                f.write(video_file.read())

            # Scan for QR codes in the video
            qr_codes = scan_qr(TEMP_VIDEO_PATH)

            # Display the detected QR codes
            for qr_code in qr_codes:
                if st.session_state.search_code.lower() == qr_code.lower():
                    st.session_state.search_code_found = True
                    st.success(video_file.name + " contains the QR code: " + qr_code)
                    break

            # Remove the temporary video file
            os.remove(TEMP_VIDEO_PATH)

        end_time = time.time()
        processing_time = end_time - start_time
        st.session_state.scanning_text.info(
            f"Processing time: {processing_time:.2f} seconds."
        )
        st.session_state.scanning_image.empty()

        if not st.session_state.search_code_found:
            st.warning(
                f"No video files containing the QR code {st.session_state.search_code} were found."
            )


def main():
    st.sidebar.title("Which video files contain the QR code?")

    # Search box to enter the QR code to search for
    st.session_state.search_code = st.sidebar.text_input(
        "QR code",
        "",
        placeholder="SPXVN0413xxxxxxxx",
        help="Enter the QR code to search for in the video files.",
    )

    # Frame rate slider to adjust the frame rate of the video
    st.session_state.frame_rate = st.sidebar.slider(
        "Frame rate",
        1,  # min value
        60,  # max value
        10,  # default value
        1,  # step
        help="Adjust the frame rate to scan the video. Higher frame rate may speed up the scanning process but provide less accurate results.",
    )

    st.sidebar.info(
        "Blue color text indicates the QR code detected in the video. Green color text indicates the QR code matches the search code."
    )

    # File uploader to select a video file
    with st.expander("Select video files", expanded=True):
        st.session_state.video_files = st.file_uploader(
            "Select video files",
            type=["mp4"],
            accept_multiple_files=True,
            label_visibility="collapsed",
        )

    # Scan the video files for the QR code
    if st.session_state.video_files and st.session_state.search_code:
        scan_video_files()
    else:
        st.warning("Please enter a QR code and upload video files to scan.")


if __name__ == "__main__":
    main()
