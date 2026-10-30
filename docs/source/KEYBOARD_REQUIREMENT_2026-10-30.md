# Critical Product Requirement: System-Wide Proofread Keyboard Integration

## 1. Core Vision

Proofread must eventually be accessible directly from the native keyboard experience on my phone.

I do NOT want Proofread to be an application that requires me to:
1. Open a separate app.
2. Copy an entire conversation.
3. Paste it into Proofread.
4. Generate a response.
5. Copy the response.
6. Return to the original messaging application.

Instead, I want Proofread to be integrated into the keyboard experience so I can access its AI capabilities while communicating naturally across different applications.

### Desired user experience

Imagine using the regular iPhone keyboard.

Near the dictation/microphone button or another convenient location on the keyboard, there is a dedicated Proofread button.

When I tap it:
- Proofread opens its AI assistance interface.
- It analyzes the text currently available to it.
- It uses my personalized writing profile.
- It considers the conversation context when available.
- It allows me to specify my intended response or communication goal.
- It generates three personalized response suggestions.
- I select one.
- The suggestion is inserted into the current text field or copied for insertion.
- I can edit it before sending.

The interaction should feel like a natural extension of the keyboard rather than switching between multiple applications.

## 2. Cross-Application Compatibility

The primary goal is to make Proofread usable across as many iOS applications as technically possible.

At minimum, investigate compatibility with:

- Apple Messages / iMessage.
- Snapchat.
- WhatsApp.
- Instagram DMs.
- Facebook Messenger.
- Hinge.
- Tinder.
- Discord.
- Telegram.
- Other applications that support standard iOS text input.

The keyboard should not be designed exclusively around iMessage.

It should be a reusable system-wide keyboard extension that can operate in different applications without requiring a separate integration for every messaging platform.

### Important technical requirement

Investigate the actual iOS keyboard-extension APIs and limitations.

Determine:
- Which applications permit third-party keyboards.
- Which applications restrict or disable third-party keyboards.
- Whether the keyboard works in secure text fields.
- Whether the keyboard works in search fields and other input types.
- Whether the keyboard can read the text currently being composed.
- Whether it can access surrounding text through the documented iOS APIs.
- Whether it can insert generated responses into the active text field.
- Whether Full Access is required for network-based AI functionality.
- What happens when the keyboard is dismissed or the user switches applications.

Do not claim universal compatibility without verifying it.

If an application blocks third-party keyboards, clearly document that limitation and investigate alternative workflows.

## 3. Keyboard Interface Design

Design the Proofread button to feel like part of the native iOS keyboard.

It should be accessible without taking up excessive screen space.

Investigate the best placement:
- Near the dictation button.
- In the keyboard's accessory area.
- In a dedicated keyboard toolbar.
- Another location supported by Apple's keyboard-extension framework.

Do not compromise the native typing experience.

### When the Proofread button is selected

The interface should offer:

1. Generate a response.
2. Rewrite my draft.
3. Change my intended tone or goal.
4. View three personalized suggestions.
5. Regenerate suggestions.
6. Insert the selected suggestion into the active text field.

Keep the experience fast, intuitive, and visually consistent with iOS.

The user should always remain in control of what gets inserted and sent.

## 4. Conversation Context and AI Intelligence

The keyboard must use the information actually available to it.

A major challenge is that a third-party keyboard does not automatically have unrestricted access to the entire conversation in another application.

Design a context strategy that works within Apple's restrictions.

Consider combining:
- Text currently being composed.
- Text immediately before the cursor, when available.
- User-provided conversation context.
- Previously imported message history.
- Relationship-specific profiles.
- User-defined communication goals.
- Context stored securely in the Proofread application.

Investigate whether the standalone Proofread application can serve as the central location for managing personal message history, writing profiles, and relationship context.

When sufficient conversational context is unavailable, provide a convenient way for the user to supply it rather than pretending the AI understands the conversation.

## 5. Personalization Must Remain Central

The keyboard is simply the interface through which users access Proofread.

The intelligence must remain centralized in the existing personalization and AI architecture.

Every suggestion should use the same underlying:
- Writing-style profile.
- Relationship-specific preferences.
- Personalization system.
- Context retrieval system.
- Response generation engine.
- Feedback and learning mechanisms.

Do not create an entirely separate AI system for the keyboard.

A user should receive consistent personalization whether using Proofread through its standalone application or keyboard extension.

## 6. Technical Architecture Investigation

Evaluate the best implementation using Apple's supported development technologies.

Investigate:
- Swift and SwiftUI.
- Custom iOS keyboard extensions.
- UIInputViewController.
- UITextDocumentProxy.
- Keyboard extension lifecycle and memory constraints.
- App Groups for sharing appropriate data between the main application and extension.
- Secure authentication.
- Network requests from keyboard extensions.
- Full Access permissions and associated privacy implications.
- Backend API integration.
- Communication between the main app and keyboard extension.

Determine which responsibilities should live inside the keyboard and which should remain in the main application or backend.

The keyboard should ideally remain lightweight.

Expensive AI processing, message-history analysis, personalization, and response generation should be handled through the appropriate backend or shared application architecture rather than attempting to perform everything inside the keyboard extension.

## 7. Approval Before Major Changes

Before implementing the keyboard extension:

1. Evaluate the existing Proofread architecture.
2. Determine whether it can support a keyboard extension.
3. Identify any required architectural changes.
4. Explain the implementation requirements.
5. Identify Apple's technical restrictions.
6. Present the proposed architecture.
7. Estimate development complexity and potential ongoing costs.

Wait for my approval before making major architectural changes.

Do not replace working components unnecessarily.

## 8. Revised Development Roadmap

Prioritize the project in this order:

**Phase 1 — Personalization foundation**
- Import personal message history.
- Build my writing profile.
- Establish relationship-specific personalization.

**Phase 2 — AI response generation**
- Generate three responses.
- Support rewriting.
- Incorporate conversation context.
- Test response authenticity.

**Phase 3 — System-wide keyboard prototype**
- Build a native iOS keyboard extension.
- Add the Proofread button.
- Connect it to the existing backend.
- Generate suggestions directly from the keyboard.
- Insert selected suggestions into active text fields.

**Phase 4 — Cross-application testing**
- Test Messages.
- Test WhatsApp.
- Test Snapchat.
- Test Instagram.
- Test Hinge.
- Test other supported messaging applications.

Document which applications work, which have restrictions, and what workarounds are available.

**Phase 5 — Personal daily-use testing**
- Use Proofread in real conversations.
- Collect feedback.
- Identify latency and usability issues.
- Improve personalization based on actual usage.

**Phase 6 — Product refinement**
- Improve keyboard design.
- Optimize response generation speed.
- Improve context retrieval.
- Improve privacy and reliability.
- Prepare for a broader public release.

## 9. Definition of Success

The prototype should eventually allow me to:

1. Open virtually any supported messaging application.
2. Bring up the normal iOS keyboard.
3. Tap a dedicated Proofread button.
4. Generate responses using my personalized writing profile.
5. Choose between three suggestions.
6. Insert the selected response directly into the message field.
7. Edit and send it normally.

I should not need to leave the messaging application to use Proofread.

**The ultimate product vision is a personalized AI communication assistant that travels with the user across their phone, regardless of which messaging application they use.**