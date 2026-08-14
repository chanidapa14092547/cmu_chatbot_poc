import Foundation
import Vision
import AppKit

let arguments = CommandLine.arguments
if arguments.count < 2 {
    print("Usage: swift ocr_vision.swift <image_path>")
    exit(1)
}
let imagePath = arguments[1]
let url = URL(fileURLWithPath: imagePath)

guard let image = NSImage(contentsOf: url),
      let cgImage = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
    print("Failed to load image at \(imagePath)")
    exit(1)
}

let requestHandler = VNImageRequestHandler(cgImage: cgImage, options: [:])
let request = VNRecognizeTextRequest { (request, error) in
    if let error = error {
        print("Error: \(error.localizedDescription)")
        return
    }
    
    guard let observations = request.results as? [VNRecognizedTextObservation] else {
        return
    }
    
    var extractedText = ""
    for observation in observations {
        guard let topCandidate = observation.topCandidates(1).first else { continue }
        extractedText += topCandidate.string + "\n"
    }
    print(extractedText)
}

do {
    if #available(macOS 11.0, *) {
        // macOS 11 doesn't support Thai natively in Vision. Thai was added in macOS 13 or 14. 
        // But let's try with default which might automatically detect languages in newer macOS.
        // We will just let it use default languages first.
    }
    try requestHandler.perform([request])
} catch {
    print("Failed to perform OCR: \(error.localizedDescription)")
}
