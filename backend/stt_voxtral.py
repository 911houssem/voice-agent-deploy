import torch
import numpy as np
from transformers import VoxtralRealtimeForConditionalGeneration, AutoProcessor
from mistral_common.tokens.tokenizers.audio import Audio

class VoxtralSTT:
    def __init__(self, model_path: str):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.bfloat16 if self.device == "cuda" else torch.float32
        print(f"[VOXTRAL] Using {dtype} on {self.device}")
        self.model = VoxtralRealtimeForConditionalGeneration.from_pretrained(
            model_path,
            torch_dtype=dtype,
            device_map="auto" if self.device == "cuda" else None,
            low_cpu_mem_usage=True,
        )
        self.processor = AutoProcessor.from_pretrained(model_path)
        self.sr = self.processor.feature_extractor.sampling_rate

    @torch.inference_mode()
    def transcribe_wav(self, wav_path: str):
        audio = Audio.from_file(wav_path, strict=False)
        audio.resample(self.sr)
        inputs = self.processor(audio.audio_array, return_tensors="pt")
        if self.device == "cuda":
            inputs = inputs.to(self.model.device)
        outputs = self.model.generate(**inputs, do_sample=False)
        text = self.processor.batch_decode(outputs, skip_special_tokens=True)[0]
        return text.strip()
