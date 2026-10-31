# Organize the owner's Mac demo folders

This is a local helper, not remote Mac access. Downloadable distribution includes
a `notes-test` updater. Repository execution without that payload fails before
moving anything. It never automatically runs the updater or changes app source.

Only explicit historical demo/download names in `OLD_NAMES` are archived. The
working `Documents/Proofread-Capture-Study` path and Xcode signing remain intact.
Unrelated folders/files are untouched. A dated archive records each move in
`MOVED.json`; nothing is deleted. Known symlinks are rejected before moves.

After cleanup use `START-HERE.txt` in the working project: apply its local updater,
open the existing Xcode project and Command-R. No new download is needed for the
Notes test. An unexpected source edit still causes the updater to refuse safely.
