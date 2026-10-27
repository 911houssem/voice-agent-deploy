import sys
from pathlib import Path

class SilmaTTS:
    def __init__(self, silma_dir: str):
        self.silma_dir = Path(silma_dir)
        src_path = self.silma_dir / "src"
        if src_path.exists():
            if str(src_path) not in sys.path:
                sys.path.insert(0, str(src_path))
            print(f"[SILMA] Added to path: {src_path}")
        else:
            print(f"[SILMA] WARNING: src/ not found in {self.silma_dir}, trying direct import")

        try:
            from silma_tts.api import SilmaTTS as _SilmaTTS
            self.tts = _SilmaTTS()
            print("[SILMA] API imported successfully")
        except Exception as e:
            raise RuntimeError(f"فشل استيراد silma_tts.api: {e}\nتحقق من models/silma-tts/src وجوده")

    def synthesize(self, text: str, ref_audio: str, ref_text: str, out_path: str):
        wav, sr, spec = self.tts.infer(
            ref_file=ref_audio,
            ref_text=ref_text,
            gen_text=text.strip(),
            file_wave=str(out_path),
            seed=None,
            speed=1.0,
        )
        return str(out_path), sr
