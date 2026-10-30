# Synthetic keyboard feasibility spike

Owner approval: October 30, for a **narrow synthetic prototype** only. No production
keyboard, profile/history/session design, backend context change or paid service
was authorized. This implementation is an offline platform harness, not AI.

## What is included

- A `UIInputViewController` extension target embedded by the containing app.
- Minimal lowercase ASCII keys, space, delete, return and next-keyboard control.
  This is not Apple's keyboard or a full autocorrect/dictation implementation.
- Explicit Proofread panel action, available text-field context capture, generate
  and rewrite **fixtures**, three suggestions and user-selected insertion.
- A shared Foundation safety model: missing/oversized context fails closed;
  changed field/cursor/selection/document identity invalidates suggestions;
  successful insertion selection consumes the suggestions to prevent reuse.
- Permission-state display and lifecycle invalidation. No App Group, Keychain,
  clipboard scanning, network service, raw text log or persistent storage.

`RequestsOpenAccess` is enabled in the extension declaration only so permission
states can be tested. **Granting it is optional.** Both sets of sample suggestions
are local and work without it. There is no cloud consent or history-import flow;
Full Access is not treated as permission for either. Use invented text in a
non-sensitive test field. Proxy context is limited editable-field context, not a
chat transcript, and a snapshot match cannot prove unseen document contents.

The rewrite fixture does not rewrite the actual field. The harness always inserts
at the active cursor; it refuses insertion while host text is selected (because
`insertText` can replace that selection). Place the cursor first. It does not
delete or replace the whole draft and
never presses Send. Do not infer personalization, relationship awareness, AI quality
or whole-conversation access from this spike.

## Build on a Mac

Use the full repository branch `codex/synthetic-keyboard-prototype`, or the supplied
native-source bundle, with Xcode and XcodeGen installed. From its root:

```sh
bash ios/scripts/validate-macos.sh
```

This unsigned simulator build should include the embedded extension. It has not
been run in Linux; Swift Package tests compile the Foundation model only. If
signing is required for physical-device installation, configure the same team for
app and extension with distinct app bundle identifiers. No App Group entitlement
is needed. Do not alter a production app's identifiers or publish this spike.

After generating `ios/Proofread.xcodeproj`, open it in Xcode, choose the Proofread
scheme and an iOS 17+ simulator/device, and run the app. Enable **Proofread
Prototype** through iOS Settings → General → Keyboard → Keyboards → Add New
Keyboard. Use the globe/menu control to select it in a standard editable field.
Settings labels may vary by iOS version. Start without Full Access.

## Record actual results, not assumptions

1. In an invented draft, type using sample keys; test space/delete/return and
   switching back to the system keyboard. Verify no automatic requests or inserts.
2. Open Proofread, capture the available field context, select sample generate/
   rewrite mode and inspect three explicitly marked fixture suggestions. Check
   missing-context state if the host exposes none.
3. Select a candidate. Confirm it inserts exactly once at the active position,
   without auto-send or replacing unrelated text. Active text selection must block
   insertion until you place the cursor and capture again. Verify another tap cannot insert
   old suggestions again.
4. Capture again, then move the cursor, change selection/text, switch fields/apps,
   dismiss/reopen or rotate. Old suggestions must clear or insertion must fail.
   Test identical-looking text in different documents where document IDs differ.
5. Toggle Full Access in settings only if desired. Verify the displayed state,
   sample availability without permission and invalidation across dismissal.
   No network call is expected in either state.
6. Test secure/password and phone-pad controls as negative cases: accept system
   keyboard substitution, never bypass restrictions. Record ordinary search fields
   separately, including any host opt-out.
7. Record device/iOS/host app version, context/selection availability, insertion,
   lifecycle and layout/accessibility results. Verify small screens and large text.
   Report failures; do not submit private messages or unredacted screenshots.

All named messaging apps in `KEYBOARD_PROPOSAL.md` remain untested until this
matrix is completed. Simulator success in one field does not establish device or
cross-app compatibility. Current official Apple documentation remains blocked
by the environment proxy; refresh its contract and App Review requirements on an
accessible network before accepting the platform integration.
