import webrtcvad

class VAD:
    def __init__(self, aggressiveness: int = 2, frame_duration_ms: int = 30, sample_rate: int = 16000):
        self.vad = webrtcvad.Vad(aggressiveness)
        self.frame_duration_ms = frame_duration_ms
        self.sample_rate = sample_rate

    def is_speech(self, pcm_bytes: bytes):
        try:
            if len(pcm_bytes) == 0:
                return False
            return self.vad.is_speech(pcm_bytes, self.sample_rate)
        except Exception:
            return False
