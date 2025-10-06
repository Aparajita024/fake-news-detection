import { Sun, Moon, LogIn } from "lucide-react";
import { Button } from "./ui/button";

// Replace these with your actual hosted image URLs
const LogoLight = "https://ik.imagekit.io/89d6zwqgh/NEW.png?updatedAt=1759701382580"; 
const LogoDark = "https://ik.imagekit.io/89d6zwqgh/hoshiyaar_khabardaar_darkmode-removebg-preview.png?updatedAt=1759701178225https://ik.imagekit.io/89d6zwqgh/hoshiyaar_khabardaar_darkmode-removebg-preview.png?updatedAt=1759701324241";  // Replace with your dark mode logo URL

interface HeaderProps {
  isDark: boolean;
  onThemeToggle: () => void;
}

export function Header({ isDark, onThemeToggle }: HeaderProps) {
  return (
    <header
  className="max-width-xl fixed left-0 right-0 z-50 backdrop-blur-xl bg-white/30 dark:bg-black/30"
  style={{ top: "20px", backdropFilter: "blur(10px)" }}
>

<div
  className="max-w-5xl mx-auto px-10 py-5 flex items-center justify-between relative z-50 rounded-full border border-border shadow-lg"
  style={{
    paddingTop: "10px",
    paddingBottom: "10px",
  }}
>


        {/* Logo */}
        <div className="flex items-center gap-10" style={{ paddingLeft: "24px" }}>
          <div className="h-10 flex items-center px-2 rounded">
            <img 
              src={isDark ? LogoDark : LogoLight} 
              alt="Logo" 
              className="h-10 w-auto object-contain"
              onError={(e) => {
                console.error("Image failed to load:", e.currentTarget.src);
                e.currentTarget.style.display = 'none';
                e.currentTarget.parentElement!.innerHTML = `<span class="text-xl font-bold">${isDark ? '🌙' : '☀️'} Logo</span>`;
              }}
            />
          </div>
        </div>

        {/* Right side buttons */}
        <div className="flex items-center gap-3 "style={{ paddingRight: "24px" }}>
          <Button
            onClick={onThemeToggle}
            variant="ghost"
            size="sm"
          >
            {isDark ? (
              <Sun size={18} />
            ) : (
              <Moon size={18} />
            )}
          </Button>

          <Button
            variant="ghost"
            size="sm"
          >
            <LogIn size={16} className="mr-2" />
            Sign In
          </Button>
        </div>
      </div>
    </header>
  );
}