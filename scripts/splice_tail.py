"""Replace the end of a silent render with newly rendered frames, without rendering the whole film again.
Typical use: a link on the end card changed. Render only the changed frames
(`npx remotion render <Comp> tail.mp4 --frames=<from>-<last> --muted`), then splice them onto the old render. The
result is re-encoded once (H.264, CRF 17) and checked to have exactly the old frame count before it replaces anything.
Mix the soundtrack again afterwards.
Usage: python -I splice_tail.py <full_silent.mp4> <tail.mp4> <from_frame> [<out.mp4>]
       (without out.mp4, the full render is replaced in place once the check passes)"""
import os
import shutil
import subprocess
import sys


def frames(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
                          "stream=nb_read_frames", "-of", "csv=p=0", path], capture_output=True, text=True, check=True).stdout
    return int(out.strip().strip(","))  # csv output ends with a comma


full, tail, start = sys.argv[1], sys.argv[2], int(sys.argv[3])
dest = sys.argv[4] if len(sys.argv) > 4 else full
want = frames(full)
tmp = os.path.splitext(dest)[0] + ".splicing.mp4"
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", full, "-i", tail, "-filter_complex",
                f"[0:v]trim=end_frame={start},setpts=PTS-STARTPTS[a];[1:v]setpts=PTS-STARTPTS[b];[a][b]concat=n=2:v=1:a=0[v]",
                "-map", "[v]", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p",
                "-movflags", "+faststart", tmp], check=True, stdin=subprocess.DEVNULL)
got = frames(tmp)
if got != want:
    os.remove(tmp)
    sys.exit(f"spliced video has {got} frames, the original {want}; nothing replaced (is the tail the right length?)")
shutil.move(tmp, dest)
print(f"{dest}: frames 0-{start - 1} from {os.path.basename(full)}, {start}-{want - 1} from {os.path.basename(tail)}")
