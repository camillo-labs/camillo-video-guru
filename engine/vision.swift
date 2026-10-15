// Apple Vision helper for the edit engine (macOS only).
//   vision faces img1.png img2.png ...     prints JSON: [{"file":..., "faces":[[cx,cy,w,h],...]}], coordinates 0..1, y down
//   vision mask indir outdir [quality]     writes outdir/<same name>.png, 8-bit person masks at the input size
// Build: swiftc -O vision.swift -o bin/vision
import Foundation
import Vision
import CoreImage
import AppKit

func loadCG(_ path: String) -> CGImage? {
    guard let img = NSImage(contentsOfFile: path) else { return nil }
    var r = CGRect(origin: .zero, size: img.size)
    return img.cgImage(forProposedRect: &r, context: nil, hints: nil)
}

let args = CommandLine.arguments
if args.count < 3 { FileHandle.standardError.write("usage: vision faces|mask ...\n".data(using: .utf8)!); exit(2) }

if args[1] == "faces" {
    var out: [[String: Any]] = []
    for p in args[2...] {
        guard let cg = loadCG(p) else { continue }
        let req = VNDetectFaceRectanglesRequest()
        let h = VNImageRequestHandler(cgImage: cg, options: [:])
        try? h.perform([req])
        var fs: [[Double]] = []
        for o in (req.results ?? []) {
            let b = o.boundingBox
            fs.append([Double(b.midX), Double(1.0 - b.midY), Double(b.width), Double(b.height)])
        }
        out.append(["file": p, "faces": fs])
    }
    let d = try! JSONSerialization.data(withJSONObject: out)
    print(String(data: d, encoding: .utf8)!)
} else if args[1] == "mask" {
    let indir = args[2], outdir = args[3]
    let q: VNGeneratePersonSegmentationRequest.QualityLevel = (args.count > 4 && args[4] == "accurate") ? .accurate : .balanced
    try? FileManager.default.createDirectory(atPath: outdir, withIntermediateDirectories: true)
    let files = (try? FileManager.default.contentsOfDirectory(atPath: indir))?.filter { $0.hasSuffix(".png") || $0.hasSuffix(".jpg") }.sorted() ?? []
    let ctx = CIContext()
    for f in files {
        guard let cg = loadCG(indir + "/" + f) else { continue }
        let req = VNGeneratePersonSegmentationRequest()
        req.qualityLevel = q
        req.outputPixelFormat = kCVPixelFormatType_OneComponent8
        let h = VNImageRequestHandler(cgImage: cg, options: [:])
        try? h.perform([req])
        guard let pb = req.results?.first?.pixelBuffer else { continue }
        var ci = CIImage(cvPixelBuffer: pb)
        let sx = CGFloat(cg.width) / ci.extent.width, sy = CGFloat(cg.height) / ci.extent.height
        ci = ci.transformed(by: CGAffineTransform(scaleX: sx, y: sy))
        let cs = CGColorSpaceCreateDeviceGray()
        if let data = ctx.pngRepresentation(of: ci, format: .L8, colorSpace: cs, options: [:]) {
            try? data.write(to: URL(fileURLWithPath: outdir + "/" + (f as NSString).deletingPathExtension + ".png"))
        }
    }
}
