"""Where things live. The repo holds code, style definitions, docs and small fixtures. Rendered video,
source footage and the generated test material do not go in git, so they are found through MEDIA_ROOT.

    ROOT        the repo root
    STYLES      ROOT/styles, one folder per style, each with a style.json
    SFX         ROOT/sfx by default, or $SFX_LIBRARY (the sound effect WAV files are not in git)
    MEDIA_ROOT  $VIDEO_ENGINE_MEDIA, else Cam's design-library edits folder on this Mac if it exists, else None.
                Relative media paths in an edl (for example _testdata/music/house128.wav or
                tests/green-label/assets/music/x.mp3) are relative to it.
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STYLES = ROOT / 'styles'
DEFAULT_MEDIA = Path('/Users/student/dev/design-library/edits')


def _media_root():
    env = os.environ.get('VIDEO_ENGINE_MEDIA')
    if env:
        return Path(env).expanduser()
    return DEFAULT_MEDIA if DEFAULT_MEDIA.is_dir() else None


MEDIA_ROOT = _media_root()
SFX = Path(os.environ.get('SFX_LIBRARY', ROOT / 'sfx'))


def media(rel):
    """Resolve a media path. Absolute paths and paths that already exist are returned as they are,
    otherwise it is looked up under MEDIA_ROOT. Returns a Path, which may not exist."""
    p = Path(rel)
    if p.is_absolute() or p.exists() or MEDIA_ROOT is None:
        return p
    return MEDIA_ROOT / p


def media_available(*rels):
    """True when every named media path exists. Tests use this to skip with a clear message."""
    return all(media(r).exists() for r in rels)


def skip_reason(*rels):
    miss = [str(media(r)) for r in rels if not media(r).exists()]
    if not miss:
        return None
    return ('media not found: ' + ', '.join(miss) + '. Set VIDEO_ENGINE_MEDIA to the folder that holds '
            '_testdata/ and tests/*/assets/ (see fixtures/README.md).')
