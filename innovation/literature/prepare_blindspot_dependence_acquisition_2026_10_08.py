"""Create an independent read-only primary acquisition script without changing the old one."""
import ast
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    old = ROOT/'literature/fetch_distortion_perception_primary_2026_10_08.py'
    dest = ROOT/'literature/fetch_blindspot_dependence_primary_2026_10_08.py'
    assert not dest.exists()
    text = old.read_text(encoding='utf-8')
    replacements = [
        ('distortion_perception_primary_2026-10-08', 'blindspot_dependence_primary_2026-10-08'),
        ("('perception_distortion', 'https://arxiv.org/pdf/1711.06077')", "('noise2void', 'https://arxiv.org/pdf/1811.10980')"),
        ("('rate_distortion_perception', 'https://arxiv.org/pdf/1901.07821')", "('noise2same', 'https://arxiv.org/pdf/2010.12062')"),
        ('2026-10-08_distortion_perception_primary_protocol.md', '2026-10-08_blindspot_dependence_primary_protocol.md')]
    for a, b in replacements:
        assert text.count(a) == 1, a
        text = text.replace(a, b)
    ast.parse(text)
    with dest.open('x', encoding='utf-8') as f:
        f.write(text)
    print('Created separate Noise2Void/Noise2Same public-author-PDF acquisition script', flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
