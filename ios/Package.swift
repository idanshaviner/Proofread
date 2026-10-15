// swift-tools-version: 5.9
import PackageDescription

// Compile the same Foundation sources that the iOS app uses, without importing
// SwiftUI/UIKit. This supports Linux contract tests, not iOS build verification.
let package = Package(
    name: "ProofreadNetworking",
    platforms: [.iOS(.v17), .macOS(.v14)],
    products: [.library(name: "ProofreadNetworking", targets: ["ProofreadNetworking"])],
    targets: [
        .target(
            name: "ProofreadNetworking",
            path: "Proofread",
            exclude: ["Views", "ProofreadApp.swift"],
            sources: ["Models", "Services"]
        ),
        .testTarget(
            name: "ProofreadNetworkingTests",
            dependencies: ["ProofreadNetworking"],
            resources: [.copy("Fixtures")]
        )
    ]
)
