"""Archive only named Proofread demo artifacts; never delete or touch signing."""
from datetime import datetime
from pathlib import Path
import json
import shutil
import sys

# Explicit names from this project's downloads. No broad Proofread* matching.
OLD_NAMES = (
    'Proofread-preview', 'Proofread-preview 2', 'Proofread-keyboard-prototype',
    'Proofread-local-preview.zip', 'Proofread-local-preview-fixed-2026-10-30.zip',
    'Proofread-preview-optimized-2026-10-30.zip',
    'Proofread-keyboard-prototype-source-2026-10-30.zip', 'Proofread-Capture-Study.zip',
    'Proofread-Observation-Fix', 'Proofread-Observation-Fix.zip',
    'Proofread-Capture-Build-Fix', 'Proofread-Capture-Build-Fix.zip',
    'Proofread-Clean-Retry', 'Proofread-Clean-Retry.zip',
    'Proofread-Notes-Test', 'Proofread-Notes-Test.zip',
    'inspect-capture-sdk.sh', 'Proofread-context-capture-research.md',
    'Proofread-keyboard-proposal-2026-10-30.md',
    'Proofread-repository-assessment-2026-10-30.md',
    'Proofread-performance-cost-review-2026-10-30.md',
)


def organize(documents, helper_dir):
    documents, helper_dir = Path(documents).resolve(), Path(helper_dir).resolve()
    project = documents / 'Proofread-Capture-Study'
    pbx = project / 'ios/CaptureStudy/ProofreadCaptureStudy.xcodeproj/project.pbxproj'
    if project.is_symlink() or not pbx.is_file():
        raise ValueError('Working Proofread-Capture-Study Xcode project not found. Nothing changed.')
    for name in OLD_NAMES:
        if (documents / name).is_symlink():
            raise ValueError('A known artifact is a symbolic link. Nothing changed.')
    update = helper_dir / 'notes-test'
    if not (update / 'apply.command').is_file() or not (update / 'manifest.json').is_file():
        raise ValueError('Extract the complete organizer ZIP first. Nothing changed.')
    tool_dir = project / 'tools'
    if tool_dir.is_symlink() or (tool_dir / 'notes-test').is_symlink():
        raise ValueError('Project tools contain a symbolic link. Nothing changed.')
    if (project / 'START-HERE.txt').is_symlink():
        raise ValueError('START-HERE is a symbolic link. Nothing changed.')
    archive_parent = documents / 'Proofread Archive' 
    if archive_parent.is_symlink():
        raise ValueError('Archive directory is a symbolic link. Nothing changed.')
    archive_parent.mkdir(exist_ok=True)
    # Exclusive creation avoids overwriting an older archive on repeat runs.
    import tempfile
    archive = Path(tempfile.mkdtemp(prefix=datetime.now().strftime('%Y-%m-%d_'), dir=str(archive_parent)))
    moved = []
    journal = archive / 'MOVED.json'

    def move(source, destination):
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(destination))
        moved.append({'from': str(source), 'to': str(destination)})
        journal.write_text(json.dumps(moved, indent=2), encoding='utf-8')

    for name in OLD_NAMES:
        source = documents / name
        if source.exists():
            move(source, archive / 'old-downloads' / name)
    tool_dir.mkdir(exist_ok=True)
    target = tool_dir / 'notes-test'
    if target.exists():
        move(target, archive / 'previous-notes-tool')
    shutil.copytree(str(update), str(target))
    start = project / 'START-HERE.txt'
    if start.exists():
        if start.is_symlink():
            raise ValueError('START-HERE is a symbolic link; not overwritten. Other moves are recorded in archive.')
        move(start, archive / 'previous-START-HERE.txt')
    start.write_text('''PROOFREAD — CURRENT TEST

This is your working capture-study project. Keep this folder in Documents.
Older demos/downloads are in Documents/Proofread Archive. Nothing was deleted.

NEXT RUN:
1. In Terminal:
   cd ~/Documents/Proofread-Capture-Study
   bash tools/notes-test/apply.command
   open ios/CaptureStudy/ProofreadCaptureStudy.xcodeproj
2. In Xcode select your iPhone and press Command-R. No XcodeGen regeneration.
3. Use only a fresh invented Notes phrase, never real chats. Enable the Notes test,
   confirm synthetic content, start sharing, then tap Capture in 5 seconds and
   switch to your note. Return within20 seconds, inspect output and press Stop.
4. Verify system sharing ended. No AI replies or keyboard context transfer yet.

The update tool checks source hashes and backs up changed files. Signing stays intact.
Cross-app behavior remains an experiment, not a verified capability.
''', encoding='utf-8')
    if helper_dir.parent == documents and helper_dir.name == 'Proofread-Organizer':
        move(helper_dir, archive / 'organizer-used')
    for name in ('Proofread-Organizer.zip',):
        item = documents / name
        if item.is_file() and not item.is_symlink():
            move(item, archive / name)
    journal.write_text(json.dumps(moved, indent=2), encoding='utf-8')
    return project, archive


if __name__ == '__main__':
    try:
        project, archive = organize(Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / 'Documents',
                                    Path(__file__).resolve().parent)
    except (ValueError, OSError) as error:
        sys.exit(str(error))
    print('Organized. Working project: ' + str(project))
    print('Older items moved, not deleted: ' + str(archive))
    print('Read START-HERE.txt in the working project. Source and signing were not changed.')
