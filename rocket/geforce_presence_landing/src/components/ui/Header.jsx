import React, { useState } from 'react';
import Icon from '../AppIcon';
import Button from './Button';

const Header = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-background/95 backdrop-blur-md border-b border-border">
      <div className="w-full">
        <div className="flex items-center justify-between h-16 px-6">
          {/* Logo */}
          <div className="flex items-center space-x-3">
            <div className="relative">
              <div className="w-8 h-8 bg-gradient-to-br from-primary to-secondary rounded-lg flex items-center justify-center glow-primary">
                <Icon name="Zap" size={20} color="var(--color-background)" strokeWidth={2.5} />
              </div>
              <div className="absolute inset-0 bg-gradient-to-br from-primary to-secondary rounded-lg opacity-20 blur-sm"></div>
            </div>
            <div className="flex flex-col">
              <span className="text-lg font-heading font-heading-bold text-foreground">
                GeForce Presence
              </span>
              <span className="text-xs font-mono font-mono-normal text-text-secondary -mt-1">
                v2.1.0
              </span>
            </div>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            <a 
              href="#features" 
              className="text-text-secondary hover:text-primary transition-colors duration-micro font-body font-body-medium"
            >
              Features
            </a>
            <a 
              href="#installation" 
              className="text-text-secondary hover:text-primary transition-colors duration-micro font-body font-body-medium"
            >
              Installation
            </a>
            <a 
              href="#documentation" 
              className="text-text-secondary hover:text-primary transition-colors duration-micro font-body font-body-medium"
            >
              Docs
            </a>
            <a 
              href="#community" 
              className="text-text-secondary hover:text-primary transition-colors duration-micro font-body font-body-medium"
            >
              Community
            </a>
          </nav>

          {/* Desktop Actions */}
          <div className="hidden md:flex items-center space-x-4">
            <Button
              variant="ghost"
              iconName="Github"
              iconPosition="left"
              iconSize={18}
              onClick={() => window.open('https://github.com/geforce-presence', '_blank')}
              className="text-text-secondary hover:text-foreground"
            >
              GitHub
            </Button>
            <Button
              variant="default"
              iconName="Download"
              iconPosition="left"
              iconSize={18}
              className="glow-primary-hover micro-interact"
            >
              Download
            </Button>
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden">
            <Button
              variant="ghost"
              size="icon"
              onClick={toggleMobileMenu}
              className="text-text-secondary hover:text-foreground"
            >
              <Icon name={isMobileMenuOpen ? "X" : "Menu"} size={24} />
            </Button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMobileMenuOpen && (
          <div className="md:hidden border-t border-border bg-surface/95 backdrop-blur-md">
            <nav className="px-6 py-4 space-y-4">
              <a 
                href="#features" 
                className="block text-text-secondary hover:text-primary transition-colors duration-micro font-body font-body-medium py-2"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Features
              </a>
              <a 
                href="#installation" 
                className="block text-text-secondary hover:text-primary transition-colors duration-micro font-body font-body-medium py-2"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Installation
              </a>
              <a 
                href="#documentation" 
                className="block text-text-secondary hover:text-primary transition-colors duration-micro font-body font-body-medium py-2"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Documentation
              </a>
              <a 
                href="#community" 
                className="block text-text-secondary hover:text-primary transition-colors duration-micro font-body font-body-medium py-2"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Community
              </a>
              <div className="pt-4 border-t border-border space-y-3">
                <Button
                  variant="ghost"
                  iconName="Github"
                  iconPosition="left"
                  iconSize={18}
                  fullWidth
                  onClick={() => {
                    window.open('https://github.com/geforce-presence', '_blank');
                    setIsMobileMenuOpen(false);
                  }}
                  className="justify-start text-text-secondary hover:text-foreground"
                >
                  GitHub Repository
                </Button>
                <Button
                  variant="default"
                  iconName="Download"
                  iconPosition="left"
                  iconSize={18}
                  fullWidth
                  className="glow-primary-hover micro-interact"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  Download Now
                </Button>
              </div>
            </nav>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;