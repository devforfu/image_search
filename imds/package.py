import tarfile
from pathlib import Path


def create_tar(src: Path, dst: Path, exts: str='jpeg|jpg|png'):
    """Creates archive from folders with images."""

    src, dst = [Path(p) for p in (src, dst)]
    images = []

    for ext in exts.split('|'):
        for case in (ext.lower(), ext.upper()):
            for filename in src.rglob(f'*.{case}'):
                images.append(filename)

    with tarfile.TarFile(dst, 'w') as tar:
        for filename in images:
            tar.add(filename)
