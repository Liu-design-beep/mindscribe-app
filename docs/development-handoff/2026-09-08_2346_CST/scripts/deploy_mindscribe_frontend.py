from __future__ import annotations

from pathlib import Path
import re
import shutil

BUILD = Path('/home/ubuntu/lingji-resume/dist/public')
REPO = Path('/home/ubuntu/mindscribe-live-repo')
ASSET_SOURCE = Path('/home/ubuntu/webdev-static-assets/lingji-resume')
TARGETS = [REPO / 'app/frontend', REPO / 'app/web/frontend']

storage_map = {
    '/manus-storage/mindscribe-brand_4da2eb81.png': 'mindscribe-brand.png',
    '/manus-storage/mindscribe-loading_5ed0f15f.png': 'mindscribe-loading.png',
    '/manus-storage/campus-presentation_b4574c22.webp': 'campus-presentation.webp',
    '/manus-storage/profile_9688b303.webp': 'profile.webp',
    '/manus-storage/solidworks_4aba9a16.webp': 'solidworks.webp',
    '/manus-storage/control_f383f8c3.webp': 'control.webp',
    '/manus-storage/beam_b9a81eb8.webp': 'beam.webp',
    '/manus-storage/candy_e667b99d.webp': 'candy.webp',
    '/manus-storage/drone_ea894fc2.webp': 'drone.webp',
    '/manus-storage/robot-poster_f6627ea5.jpg': 'robot-poster.jpg',
    '/manus-storage/robot-demo_a6e921cd.mp4': 'robot-demo.mp4',
    '/manus-storage/salvage-poster_5b11f045.jpg': 'salvage-poster.jpg',
    '/manus-storage/salvage-demo_09b153ed.mp4': 'salvage-demo.mp4',
    '/manus-storage/Moxin-Liu-Smart-Hardware-PM-CN-20260908-v4_3ded8d47.pdf': 'Moxin-Liu-Smart-Hardware-PM-CN-20260908-v4.pdf',
    '/manus-storage/Moxin-Liu-Smart-Hardware-PM-EN-20260908-v4_8731054f.pdf': 'Moxin-Liu-Smart-Hardware-PM-EN-20260908-v4.pdf',
    '/manus-storage/running-photo_4fa2df38.webp': 'running-photo.webp',
    '/manus-storage/running-stats_eef52e4b.webp': 'running-stats.webp',
    '/manus-storage/running-recent_3a31dbde.webp': 'running-recent.webp',
    '/manus-storage/access-terminal-24_a91f6fad.webp': 'access-terminal-24.webp',
    '/manus-storage/access-terminal-5_4a716c60.webp': 'access-terminal-5.webp',
    '/manus-storage/access-terminal-7_eef7ddf5.webp': 'access-terminal-7.webp',
    '/manus-storage/access-terminal-oem_44612c23.webp': 'access-terminal-oem.webp',
    '/manus-storage/home-lock-01_5dd5c375.webp': 'home-lock-01.webp',
    '/manus-storage/home-lock-02_97790b70.webp': 'home-lock-02.webp',
    '/manus-storage/glass-lock-01_8567f1dc.webp': 'glass-lock-01.webp',
    '/manus-storage/glass-lock-02_a4635eb2.webp': 'glass-lock-02.webp',
    '/manus-storage/rv-lock-pilot_aeb4d131.webp': 'rv-lock-pilot.webp',
    '/manus-storage/rv-lock-mechanism_647bf533.webp': 'rv-lock-mechanism.webp',
    '/manus-storage/rv-lock-structure_4c825523.webp': 'rv-lock-structure.webp',
    '/manus-storage/work-access-test_760f3bc5.webp': 'work-access-test.webp',
    '/manus-storage/reader-packaged_6be97ff6.webp': 'reader-packaged.webp',
    '/manus-storage/work-issue-triage_040fb2e4.webp': 'work-issue-triage.webp',
    '/manus-storage/reader-model-01_b71d307b.webp': 'reader-model-01.webp',
    '/manus-storage/reader-model-02_1ea45829.webp': 'reader-model-02.webp',
    '/manus-storage/cloud-deep-poster-final_ba85b39e.jpg': 'cloud-deep-poster.jpg',
    '/manus-storage/cloud-deep-demo_17aee7d6.mp4': 'cloud-deep-demo.mp4',
}

source_files = {
    'mindscribe-brand.png': ASSET_SOURCE / 'mindscribe-brand.png',
    'mindscribe-loading.png': ASSET_SOURCE / 'mindscribe-loading.png',
    'campus-presentation.webp': ASSET_SOURCE / 'campus-presentation.webp',
    'profile.webp': ASSET_SOURCE / 'profile.webp',
    'solidworks.webp': ASSET_SOURCE / 'solidworks.webp',
    'control.webp': ASSET_SOURCE / 'control.webp',
    'beam.webp': ASSET_SOURCE / 'beam.webp',
    'candy.webp': ASSET_SOURCE / 'candy.webp',
    'drone.webp': ASSET_SOURCE / 'drone.webp',
    'robot-poster.jpg': ASSET_SOURCE / 'robot-poster.jpg',
    'robot-demo.mp4': ASSET_SOURCE / 'robot-demo.mp4',
    'salvage-poster.jpg': ASSET_SOURCE / 'salvage-poster.jpg',
    'salvage-demo.mp4': ASSET_SOURCE / 'salvage-demo.mp4',
    'Moxin-Liu-Smart-Hardware-PM-CN-20260908-v4.pdf': Path('/home/ubuntu/liumoxin-resume-typst/resume-cn.pdf'),
    'Moxin-Liu-Smart-Hardware-PM-EN-20260908-v4.pdf': Path('/home/ubuntu/liumoxin-resume-typst/resume-en.pdf'),
    'running-photo.webp': ASSET_SOURCE / 'running-photo.webp',
    'running-stats.webp': ASSET_SOURCE / 'running-stats.webp',
    'running-recent.webp': ASSET_SOURCE / 'running-recent.webp',
    'access-terminal-24.webp': ASSET_SOURCE / 'access-terminal-24.webp',
    'access-terminal-5.webp': ASSET_SOURCE / 'access-terminal-5.webp',
    'access-terminal-7.webp': ASSET_SOURCE / 'access-terminal-7.webp',
    'access-terminal-oem.webp': ASSET_SOURCE / 'access-terminal-oem.webp',
    'home-lock-01.webp': ASSET_SOURCE / 'home-lock-01.webp',
    'home-lock-02.webp': ASSET_SOURCE / 'home-lock-02.webp',
    'glass-lock-01.webp': ASSET_SOURCE / 'glass-lock-01.webp',
    'glass-lock-02.webp': ASSET_SOURCE / 'glass-lock-02.webp',
    'rv-lock-pilot.webp': ASSET_SOURCE / 'rv-lock-pilot.webp',
    'rv-lock-mechanism.webp': ASSET_SOURCE / 'rv-lock-mechanism.webp',
    'rv-lock-structure.webp': ASSET_SOURCE / 'rv-lock-structure.webp',
    'work-access-test.webp': ASSET_SOURCE / 'work-access-test.webp',
    'reader-packaged.webp': ASSET_SOURCE / 'reader-packaged.webp',
    'work-issue-triage.webp': ASSET_SOURCE / 'work-issue-triage.webp',
    'reader-model-01.webp': ASSET_SOURCE / 'reader-model-01.webp',
    'reader-model-02.webp': ASSET_SOURCE / 'reader-model-02.webp',
    'cloud-deep-poster.jpg': ASSET_SOURCE / 'cloud-deep-poster-final.jpg',
    'cloud-deep-demo.mp4': ASSET_SOURCE / 'cloud-deep-demo.mp4',
}

if not BUILD.exists():
    raise SystemExit(f'Missing build directory: {BUILD}')

missing = [str(path) for path in source_files.values() if not path.exists()]
if missing:
    raise SystemExit('Missing deployment assets:\n' + '\n'.join(missing))

for target in TARGETS:
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(BUILD, target)

    for obsolete in [target / '__manus__', target / '.gitkeep', target / 'favicon.svg']:
        if obsolete.is_dir():
            shutil.rmtree(obsolete)
        elif obsolete.exists():
            obsolete.unlink()

    asset_dir = target / 'portfolio-assets'
    asset_dir.mkdir(parents=True, exist_ok=True)
    for name, source in source_files.items():
        shutil.copy2(source, asset_dir / name)

    for path in target.rglob('*'):
        if path.suffix not in {'.html', '.js', '.css'}:
            continue
        text = path.read_text(encoding='utf-8')
        for storage_path, filename in storage_map.items():
            text = text.replace(storage_path, f'/portfolio-assets/{filename}')
        path.write_text(text, encoding='utf-8')

    headers = """/assets/*
  Cache-Control: public, max-age=31536000, immutable

/portfolio-assets/*
  Cache-Control: public, max-age=86400

/*.pdf
  Content-Disposition: inline
"""
    (target / '_headers').write_text(headers, encoding='utf-8')

unresolved = []
for target in TARGETS:
    for path in target.rglob('*'):
        if path.suffix not in {'.html', '.js', '.css'}:
            continue
        text = path.read_text(encoding='utf-8')
        if '/manus-storage/' in text:
            unresolved.append(str(path))
        for match in re.findall(r'/portfolio-assets/([A-Za-z0-9_.-]+)', text):
            if not (target / 'portfolio-assets' / match).exists():
                unresolved.append(f'{path}: missing {match}')

if unresolved:
    raise SystemExit('Deployment validation failed:\n' + '\n'.join(unresolved))

print('Prepared MindScribe front-end targets:')
for target in TARGETS:
    total = sum(path.stat().st_size for path in target.rglob('*') if path.is_file())
    print(f'- {target}: {total / 1024 / 1024:.2f} MiB')
print(f'- Local asset references: {len(storage_map)} mapped, 0 unresolved')
