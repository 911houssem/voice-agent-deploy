import os
import sys
import shutil
from pathlib import Path

ROOT = Path(__file__).parent
TALK_ROOT = ROOT.parent

SILMA_SRC = TALK_ROOT / "silma tts"
VOX_SRC   = TALK_ROOT / "للاستماع (ASR) Voxtral Mini 4B Realtime Arabic"

MODELS_DIR = ROOT / "models"
SILMA_DST  = MODELS_DIR / "silma-tts"
VOX_DST    = MODELS_DIR / "voxtral-ar"

def link_or_copy(src: Path, dst: Path):
    if dst.exists():
        print(f"[SKIP] {dst} موجود مسبقاً")
        return
    print(f"[LINK/COPY] {src} -> {dst}")
    try:
        os.symlink(src, dst, target_is_directory=True)
        print("  -> تم الربط الرمزي بنجاح")
    except Exception as e:
        print(f"  -> فشل الربط الرمزي، سيتم النسخ... ({e})")
        shutil.copytree(src, dst)
        print("  -> تم النسخ بنجاح")

def main():
    MODELS_DIR.mkdir(exist_ok=True)
    if not SILMA_SRC.exists():
        print(f"[ERR] لم أجد: {SILMA_SRC}")
        sys.exit(1)
    if not VOX_SRC.exists():
        print(f"[ERR] لم أجد: {VOX_SRC}")
        sys.exit(1)
    link_or_copy(SILMA_SRC, SILMA_DST)
    link_or_copy(VOX_SRC, VOX_DST)
    print("\n[OK] تم ربط النماذج جاهزة")

if __name__ == "__main__":
    main()
