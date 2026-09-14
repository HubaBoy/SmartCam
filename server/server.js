const express = require("express");
const { Server } = require("socket.io");
const PythonWorker = require("./pythonWorker");
const path = require("path");

const app = express();

const server = app.listen(3000, () => {
    console.log("Server running on http://localhost:3000");
});

const io = new Server(server, {
    cors: {
        origin: "*",
    },
});

// Serve your frontend files
app.use(express.static(path.join(__dirname, "public")));
app.use(express.static("public"));

// Start Python worker
const worker = new PythonWorker();

worker.on("data", (data) => {
    console.log("Received frame from Python");

    // Send frame to every connected browser
    io.emit("video-frame", data);
});

worker.on("close", (code) => {
    console.log("Python worker stopped:", code);
});

io.on("connection", (socket) => {
    console.log("A user connected:", socket.id);

    socket.on("disconnect", () => {
        console.log("User disconnected:", socket.id);
    });
});