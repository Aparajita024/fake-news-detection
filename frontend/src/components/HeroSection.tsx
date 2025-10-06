import { useState } from "react";
import { Link, FileUp, ImagePlus, Mic } from "lucide-react";
import { Button } from "./ui/button";

interface HeroSectionProps {
  onAnalyze: (input: string | File, type: string) => void;
  isDark: boolean;
}

export function HeroSection({ onAnalyze, isDark }: HeroSectionProps) {
  const [inputValue, setInputValue] = useState("");
  const [activeInput, setActiveInput] = useState<"text" | "url" | "image" | "voice" | "all">("text"); // <-- here
  const [file, setFile] = useState<File | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);
  const [audioChunks, setAudioChunks] = useState<Blob[]>([]);


  // Reset input when switching types
  const handleInputTypeChange = (type: "text" | "url" | "image" | "voice") => {
    if (isRecording) stopRecording();
    setActiveInput(type);
    setFile(null);
    setInputValue("");
  };

  const handleSubmit = () => {
    if ((activeInput === "image" || activeInput === "voice" || activeInput === "all") && file) {
      onAnalyze(file, activeInput);
    } else if ((activeInput === "text" || activeInput === "url") && inputValue.trim()) {
      onAnalyze(inputValue, activeInput);
    } else {
      console.error("No input provided for analysis.");
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      const chunks: Blob[] = [];

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunks.push(e.data);
      };

      recorder.onstop = () => {
        const audioBlob = new Blob(chunks, { type: "audio/webm" });
        const audioFile = new File([audioBlob], "recorded-audio.webm", { type: "audio/webm" });
        setFile(audioFile);
        setInputValue("recorded-audio.webm");
        stream.getTracks().forEach((track) => track.stop());
      };

      recorder.start();
      setMediaRecorder(recorder);
      setIsRecording(true);
      setAudioChunks(chunks);
    } catch (error) {
      console.error("Error accessing microphone:", error);
      alert("Could not access microphone. Please check permissions.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorder && isRecording) {
      mediaRecorder.stop();
      setIsRecording(false);
    }
  };

  const handleMicClick = () => {
    handleInputTypeChange("voice");
    if (isRecording) stopRecording();
    else startRecording();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      setInputValue(selectedFile.name);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const triggerFileInput = (type: "image" | "all") => {
    handleInputTypeChange(type === "image" ? "image" : "text");
    const fileInput = document.getElementById("file-input") as HTMLInputElement;
    if (fileInput) {
      fileInput.accept = type === "image" ? "image/*" : "*/*";
      fileInput.click();
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen relative z-50">
      {/* Main Headline */}
      <h1
        className="text-5xl md:text-6xl text-center mb-4 bg-gradient-to-r from-foreground to-muted-foreground bg-clip-text text-transparent max-w-3xl"
        style={{ fontFamily: "Montserrat, sans-serif" }}
      >
        What do you want to check?
      </h1>

      {/* Subtitle */}
      <p className="text-muted-foreground text-center mb-12 max-w-xl z-40">
        Verify news articles, social media posts, and claims with AI-powered fact checking.
      </p>

      {/* Input Container */}
      <div className="w-full max-w-3xl">
        <div
          className={`relative ${isDark ? "bg-card-dark/50" : "bg-card/50"} backdrop-blur-sm border border-border rounded-2xl p-2 shadow-2xl`}
        >
          {/* Textarea */}
          <textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={
              activeInput === "image" && file
                ? `Selected: ${file.name}`
                : activeInput === "image"
                ? "Click the image icon to select a file."
                : activeInput === "voice" && isRecording
                ? "Recording... Click mic icon to stop."
                : activeInput === "voice" && file
                ? `Audio recorded: ${file.name}`
                : activeInput === "voice"
                ? "Click the mic icon to start recording."
                : "Paste a URL, enter text, or describe what you want to verify..."
            }
            className="w-full bg-transparent text-foreground placeholder-muted-foreground resize-none outline-none px-4 py-3 min-h-[120px] max-h-[300px]"
            readOnly={activeInput === "image" || activeInput === "voice"}
          />

          {/* Input Type Icons */}
          <div className="flex items-center justify-between px-2 py-2 border-t border-border/50">
            <div className="flex items-center gap-2">
              <button
                onClick={() => handleInputTypeChange("url")}
                className={`p-2 rounded-lg transition-all ${
                  activeInput === "url"
                    ? "bg-blue-600/20 text-blue-400"
                    : "text-muted-foreground hover:text-foreground hover:bg-accent"
                }`}
                title="Check URL"
                aria-label="Check URL"
              >
                <Link size={18} />
              </button>

              <button
                onClick={() => triggerFileInput("image")}
                className={`p-2 rounded-lg transition-all ${
                  activeInput === "image"
                    ? "bg-blue-600/20 text-blue-400"
                    : "text-muted-foreground hover:text-foreground hover:bg-accent"
                }`}
                title="Check Image"
                aria-label="Check Image"
              >
                <ImagePlus size={18} />
              </button>

              <button
                onClick={handleMicClick}
                className={`p-2 rounded-lg transition-all flex items-center ${
                  activeInput === "voice"
                    ? "bg-blue-600/20 text-blue-400"
                    : "text-muted-foreground hover:text-foreground hover:bg-accent"
                }`}
                title="Voice Input"
                aria-label="Voice Input"
              >
                <Mic size={18} />
                {isRecording && <span className="ml-2 text-red-500">●</span>}
              </button>

              {/* All file uploads */}
              <label
                className="flex items-center gap-2 px-2 py-2 rounded-lg transition-all text-muted-foreground hover:text-foreground hover:bg-accent cursor-pointer"
                title="Upload File"
                aria-label="Upload File"
              >
                <FileUp size={18} />
                <input
                  id="file-input"
                  type="file"
                  className="hidden"
                  onChange={handleFileChange}
                  accept="*/*" // Accept all files
                />
              </label>
            </div>

            {/* Analyze Button */}
            <button
              onClick={handleSubmit}
              disabled={
                (activeInput === "text" || activeInput === "url") && !inputValue.trim()
                  ? true
                  : activeInput !== "text" && !file
              }
              className="px-6 py-2 rounded-xl transition-all text-white font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              style={{ backgroundColor: "#60a5fa" }}
              onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "#3b82f6")}
              onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "#60a5fa")}
            >
              Analyze
            </button>
          </div>
        </div>

        {/* Quick Links */}
        <div className="mt-6 flex flex-wrap justify-center gap-2 relative z-50">
          <button
            onClick={() => window.open("https://news.google.com", "_blank")}
            className="px-4 py-2 bg-accent/60 hover:bg-accent border border-border rounded-lg text-sm text-foreground transition-all"
          >
            Google News
          </button>

          <button
            onClick={() => window.open("https://inshorts.com/en/read", "_blank")}
            className="px-4 py-2 bg-accent/60 hover:bg-accent border border-border rounded-lg text-sm text-foreground transition-all"
          >
            Inshorts
          </button>

          <button
            onClick={() => window.open("https://m.dailyhunt.in/news/india/english/for+you?launch=true&mode=pwa", "_blank")}
            className="px-4 py-2 bg-accent/60 hover:bg-accent border border-border rounded-lg text-sm text-foreground transition-all"
          >
            Dailyhunt
          </button>
        </div>
      </div>
    </div>
  );
}
