const { spawn } = require("child_process");
const EventEmitter = require("events");

class PythonWorker extends EventEmitter {
    constructor() {
        super();

        this.python = spawn("python", [
            "./FaceRecognition/worker.py"
        ]);

        // Buffer for data coming from Python
        this.buffer = Buffer.alloc(0);

        this.python.stdout.on("data", (data) => {
            // Add new data to our buffer
            this.buffer = Buffer.concat([this.buffer, data]);

            // Try to extract as many complete JPEG frames as possible
            this.processBuffer();
        });

        this.python.stderr.on("data", (data) => {
            console.error("Python:", data.toString());
        });

        this.python.on("close", (code) => {
            console.log("Python worker closed:", code);
            this.emit("close", code);
        });

        this.python.on("error", (error) => {
            console.error("Python process error:", error);
        });
    }

    processBuffer() {
        while (true) {
            // We need at least 4 bytes for the frame size
            if (this.buffer.length < 4) {
                return;
            }

            // Python uses struct.pack(">I", len(data))
            // so Node must read an unsigned BIG-ENDIAN 32-bit integer.
            const frameLength = this.buffer.readUInt32BE(0);

            // Wait until we have the complete frame
            if (this.buffer.length < 4 + frameLength) {
                return;
            }

            // Extract ONLY the JPEG data
            const frame = this.buffer.subarray(
                4,
                4 + frameLength
            );

            // Remove this frame from the buffer
            this.buffer = this.buffer.subarray(
                4 + frameLength
            );

            console.log(
                "JPEG frame received:",
                frame.length,
                "bytes"
            );

            // Send the actual JPEG buffer
            this.emit("data", frame);
        }
    }

    stop() {
        if (this.python) {
            this.python.kill();
        }
    }
}

module.exports = PythonWorker;