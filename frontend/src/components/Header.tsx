import { Sun, Moon, User, LogIn } from "lucide-react";
import { Button } from "./ui/button";

interface HeaderProps {
  isDark: boolean;
  onThemeToggle: () => void;
}

export function Header({ isDark, onThemeToggle }: HeaderProps) {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-sm border-b border-border">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between relative z-50">
        {/* Logo */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-3">
  <div className="w-15 h-9 ">
    <img src="truthchecker\public\NEW.png" 
      alt="Logo" 
      className="w-15 h-9 object-contain "
    />
  </div>
</div>
          
        </div>

        {/* Right side buttons */}
        <div className="flex items-center gap-3">
          {/* Theme Toggle */}
          <Button
            onClick={onThemeToggle}
            variant="ghost"
            size="sm"
            className="p-2 hover:bg-accent"
          >
            {isDark ? (
              <Sun size={18} className="text-foreground" />
            ) : (
              <Moon size={18} className="text-foreground" />
            )}
          </Button>

          {/* Auth Buttons */}
          <Button
            variant="ghost"
            size="sm"
            className="hover:bg-accent"
          >
            <LogIn size={16} className="mr-2" />
            Sign In
          </Button>
        </div>
      </div>
    </header>
  );
}