"""Generate seamless, tempo-independent texture loops (played by a looped AudioFileProcessor note)."""
import wave
from pathlib import Path

SR = 44100


def _circ(b, a, x):
    """Filter a looped signal so the end flows into the start (run 3 cycles, keep the middle)."""
    from scipy import signal
    y = signal.lfilter(b, a, __import__("numpy").concatenate([x, x, x]))
    return y[len(x):2 * len(x)]


def _write(path, out):
    import numpy as np
    out = out * (0.9 / np.abs(out).max())
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    w = wave.open(str(path), "wb")
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((out * 32767).astype(np.int16).tobytes())
    w.close()


def _bursts(rng, n, count, amp_lo, amp_hi, dur_ms, pan_spread=0.3):
    import numpy as np
    x = np.zeros((n, 2))
    for p in rng.integers(0, n, count):
        L = max(8, int(SR * dur_ms / 1000 * rng.uniform(0.5, 1.5)))
        t = np.arange(L)
        burst = rng.standard_normal(L) * np.exp(-t / (L / 5))
        amp = rng.uniform(amp_lo, amp_hi) * rng.choice([-1, 1])
        pan = rng.uniform(0.5 - pan_spread, 0.5 + pan_spread)
        idx = (p + t) % n
        x[idx, 0] += amp * burst * (1 - pan) * 2
        x[idx, 1] += amp * burst * pan * 2
    return x


def vinyl(path, seconds=12.0, seed=7):
    import numpy as np
    from scipy import signal
    rng = np.random.default_rng(seed)
    n = int(seconds * SR)
    out = np.zeros((n, 2))
    b, a = signal.butter(2, [300 / (SR / 2), 6000 / (SR / 2)], "band")
    for c in range(2):
        h = _circ(b, a, rng.standard_normal(n))
        out[:, c] += 0.012 * h / np.std(h)                       # surface hiss
    b, a = signal.butter(2, [25 / (SR / 2), 90 / (SR / 2)], "band")
    r = _circ(b, a, rng.standard_normal(n))
    out += (0.010 * r / np.std(r))[:, None]                       # motor rumble
    cr = _bursts(rng, n, int(seconds * 38), 0.02, 0.10, 0.6) + _bursts(rng, n, int(seconds * 1.2), 0.12, 0.30, 2.5)
    b, a = signal.butter(2, [900 / (SR / 2), 9000 / (SR / 2)], "band")
    for c in range(2):
        out[:, c] += _circ(b, a, cr[:, c])                        # crackle + pops
    _write(path, out)


def rain(path, seconds=20.0, seed=11):
    import numpy as np
    from scipy import signal
    rng = np.random.default_rng(seed)
    n = int(seconds * SR)
    out = np.zeros((n, 2))
    # steady wash: band-limited noise with a slow, loop-safe swell (whole number of cycles)
    b, a = signal.butter(2, [400 / (SR / 2), 7000 / (SR / 2)], "band")
    t = np.arange(n) / SR
    swell = 1 + 0.18 * np.sin(2 * np.pi * 3 / seconds * t) + 0.08 * np.sin(2 * np.pi * 7 / seconds * t + 1.3)
    for c in range(2):
        h = _circ(b, a, rng.standard_normal(n))
        out[:, c] += 0.05 * swell * h / np.std(h)
    # distant low roar
    b, a = signal.butter(2, [60 / (SR / 2), 350 / (SR / 2)], "band")
    r = _circ(b, a, rng.standard_normal(n))
    out += (0.02 * r / np.std(r))[:, None]
    # droplets: dense small ticks + a few closer drips
    d = _bursts(rng, n, int(seconds * 260), 0.01, 0.05, 1.2, 0.45) + _bursts(rng, n, int(seconds * 6), 0.05, 0.12, 4.0, 0.4)
    b, a = signal.butter(2, [1800 / (SR / 2), 12000 / (SR / 2)], "band")
    for c in range(2):
        out[:, c] += _circ(b, a, d[:, c])
    _write(path, out)


def tape(path, seconds=12.0, seed=5):
    """Cassette hiss: soft pink-ish noise with a gentle high-mid tilt and slow flutter of the level."""
    import numpy as np
    from scipy import signal
    rng = np.random.default_rng(seed)
    n = int(seconds * SR)
    out = np.zeros((n, 2))
    t = np.arange(n) / SR
    flutter = 1 + 0.06 * np.sin(2 * np.pi * 5 / seconds * t)
    b, a = signal.butter(1, [1500 / (SR / 2), 11000 / (SR / 2)], "band")
    for c in range(2):
        h = _circ(b, a, rng.standard_normal(n))
        out[:, c] = 0.05 * flutter * h / np.std(h)
    _write(path, out)


GENERATORS = {"vinyl": vinyl, "rain": rain, "tape": tape}


def ensure(name, samples_dir, rel_file):
    """Create the texture file under <samples_dir>/<rel_file> if it does not exist yet."""
    p = Path(samples_dir) / rel_file
    if not p.exists():
        GENERATORS[name](p)
        print(f"generated texture {name}: {p}")
    return p
