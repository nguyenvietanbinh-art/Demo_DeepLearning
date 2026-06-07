import os
import subprocess


def convert_to_web_mp4(input_path, output_path):
    """
    Convert output OpenCV sang MP4 chuẩn web.
    Resize về 720px chiều ngang để tránh lỗi thiếu RAM với video 2K/4K.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    try:
        import imageio_ffmpeg
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        ffmpeg_exe = "ffmpeg"

    command = [
        ffmpeg_exe,
        "-y",
        "-i", input_path,
        "-vf", "scale=720:-2",
        "-vcodec", "libx264",
        "-preset", "veryfast",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        output_path,
    ]

    subprocess.run(command, check=True)

    if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
        raise RuntimeError("Convert video sang MP4 chuẩn web thất bại.")

    return output_path
