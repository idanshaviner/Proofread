# Local capture-study cleanup/retry

Close Xcode first. Run `bash clean-and-open.command` on the Mac; the default target
is `~/Documents/Proofread-Capture-Study`, or pass the project folder as an argument.
The downloadable helper bundle includes the authoritative corrected controller;
repository execution reads that same file without a maintained duplicate.

Known source checksums guard against overwriting unexpected edits. The helper
backs up the source and archives only project-local generated build directories.
It preserves the `.xcodeproj`, Personal Team, bundle ID and source tree; it does
not invoke XcodeGen or clear global DerivedData. Fresh unsigned device compilation
uses a project-local derived-data path, saves its log, and propagates failures.
On success it opens the existing project; select the phone and Command-R to sign,
install and run. No deployment, paid inference or recording is triggered by it.

Offline tests mock Mac tools and verify preservation and failure propagation;
actual Mac/Xcode cleanup/build remains to be run by the owner.
