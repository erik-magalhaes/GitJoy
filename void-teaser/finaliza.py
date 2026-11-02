"""Junta vídeo + trilha, normaliza para -14 LUFS (loudnorm linear, 2 passadas) e gera versão leve (<30 MB)."""
import json, os, subprocess
O = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
A = os.path.join(O, "void_audio.wav")
r = subprocess.run(["ffmpeg", "-hide_banner", "-i", A, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json",
                    "-f", "null", "-"], capture_output=True, text=True).stderr
m = json.loads(r[r.rindex("{"):])
af = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
      f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", A, "-af", af, "-ar", "48000", os.path.join(O, "void_audio_norm.wav")], check=True)
import sys
for nome in sys.argv[1:] or ("void_video", "void_video_sem_legenda"):
    v = os.path.join(O, nome + ".mp4")
    final = os.path.join(O, nome.replace("void_video", "VOID_teaser") + ".mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", v, "-i", os.path.join(O, "void_audio_norm.wav"), "-map", "0:v",
                    "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", final], check=True)
    # versão para mandar pelo chat (2 passadas a 3000k)
    leve = final.replace(".mp4", "_chat.mp4")
    for p in (1, 2):
        cmd = ["ffmpeg", "-v", "error", "-y", "-i", final, "-c:v", "libx264", "-preset", "slow", "-tune", "film",
               "-b:v", "3000k", "-pass", str(p), "-passlogfile", os.path.join(O, "x264log")]
        cmd += ["-an", "-f", "null", "/dev/null"] if p == 1 else ["-c:a", "aac", "-b:a", "160k", leve]
        subprocess.run(cmd, check=True)
    print(final, os.path.getsize(final) // 1e6, "MB;", leve, os.path.getsize(leve) // 1e6, "MB")
