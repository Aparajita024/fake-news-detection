import { useState } from "react";
import { Link2, FileText, Image, Mic } from "lucide-react";
import { Button } from "./ui/button";

interface HeroSectionProps {
  onAnalyze: (input: string | File, type: string) => void;
}

export function HeroSection({ onAnalyze }: HeroSectionProps) {
  const [inputValue, setInputValue] = useState("");
  const [activeInput, setActiveInput] = useState<string>("text");
  const [file, setFile] = useState<File | null>(null);

  const handleSubmit = () => {
    if (activeInput === 'image' || activeInput === 'voice') {
      if (file) {
        onAnalyze(file, activeInput);
      } else {
        console.error("No file selected for analysis.");
      }
    } else {
      if (inputValue.trim()) {
        onAnalyze(inputValue, activeInput);
      } else {
        // Trigger with sample data or show an error
        onAnalyze("", activeInput);
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      // For image/voice, we can immediately trigger analysis or wait for the user to click "Analyze"
      // For simplicity, we'll wait for the button click.
      // You could also show a file preview here.
      setInputValue(selectedFile.name); // Show filename in textarea
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const triggerFileInput = (type: 'image' | 'voice') => {
    setActiveInput(type);
    const fileInput = document.getElementById('file-input') as HTMLInputElement;
    if (fileInput) {
      fileInput.accept = type === 'image' ? 'image/*' : 'audio/*';
      fileInput.click();
    }
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen relative z-50">
      <input type="file" id="file-input" className="hidden" onChange={handleFileChange} />
      {/* Main Headline */}
<h1 className="text-5xl md:text-6xl text-center mb-4 bg-gradient-to-r from-foreground to-muted-foreground bg-clip-text text-black max-w-3xl" style={{ fontFamily: 'Montserrat, sans-serif' }}>

        What do you want to check?
      </h1>

      {/* Subtitle */}
      <p className="text-muted-foreground text-center mb-12 max-w-xl z-40">
        Verify news articles, social media posts, and claims with AI-powered fact checking.
      </p>

      {/* Input Container */}
      <div className="w-full max-w-3xl">
        <div className="relative bg-card/50 backdrop-blur-sm border border-border rounded-2xl p-2 shadow-2xl">
          {/* Textarea */}
          <textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={
              activeInput === 'image' ? "Click the image icon to select a file." :
              activeInput === 'voice' ? "Click the mic icon to select an audio file." :
              "Paste a URL, enter text, or describe what you want to verify..."
            }
            className="w-full bg-transparent text-foreground placeholder-muted-foreground resize-none outline-none px-4 py-3 min-h-[120px] max-h-[300px]"
            readOnly={activeInput === 'image' || activeInput === 'voice'}
          />

          {/* Input Type Icons */}
          <div className="flex items-center justify-between px-2 py-2 border-t border-border/50">
            <div className="flex items-center gap-2">
              <button
                onClick={() => setActiveInput("url")}
                className={`p-2 rounded-lg transition-all ${
                  activeInput === "url"
                    ? "bg-blue-600/20 text-blue-400"
                    : "text-muted-foreground hover:text-foreground hover:bg-accent"
                }`}
                title="Check URL"
              >
                <Link2 size={18} />
              </button>
              <button
                onClick={() => setActiveInput("text")}
                className={`p-2 rounded-lg transition-all ${
                  activeInput === "text"
                    ? "bg-blue-600/20 text-blue-400"
                    : "text-muted-foreground hover:text-foreground hover:bg-accent"
                }`}
                title="Check Text"
              >
                <FileText size={18} />
              </button>
              <button
                onClick={() => triggerFileInput('image')}
                className={`p-2 rounded-lg transition-all ${
                  activeInput === "image"
                    ? "bg-blue-600/20 text-blue-400"
                    : "text-muted-foreground hover:text-foreground hover:bg-accent"
                }`}
                title="Check Image"
              >
                <Image size={18} />
              </button>
              <button
                onClick={() => triggerFileInput('voice')}
                className={`p-2 rounded-lg transition-all ${
                  activeInput === "voice"
                    ? "bg-blue-600/20 text-blue-400"
                    : "text-muted-foreground hover:text-foreground hover:bg-accent"
                }`}
                title="Voice Input"
              >
                <Mic size={18} />
              </button>
            </div>

            <Button
              onClick={handleSubmit}
              className="text-white px-6 rounded-xl"
            >
              Analyze
            </Button>
          </div>
        </div>

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
