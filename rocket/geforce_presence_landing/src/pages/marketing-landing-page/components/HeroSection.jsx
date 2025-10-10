import React from 'react';
import Icon from '../../../components/AppIcon';
import Button from '../../../components/ui/Button';

const HeroSection = () => {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 gradient-mesh opacity-30"></div>
      <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-transparent to-secondary/10"></div>
      
      {/* Floating Particles */}
      <div className="absolute inset-0">
        <div className="absolute top-1/4 left-1/4 w-2 h-2 bg-primary rounded-full opacity-60 animate-pulse"></div>
        <div className="absolute top-3/4 right-1/4 w-1 h-1 bg-secondary rounded-full opacity-40 animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-3/4 w-3 h-3 bg-accent rounded-full opacity-30 animate-pulse delay-500"></div>
      </div>

      <div className="relative z-10 max-w-6xl mx-auto px-6 text-center">
        {/* App Logo */}
        <div className="flex justify-center mb-8">
          <div className="relative">
            <div className="w-20 h-20 bg-gradient-to-br from-primary to-secondary rounded-2xl flex items-center justify-center glow-primary">
              <Icon name="Gamepad2" size={40} color="var(--color-background)" strokeWidth={2.5} />
            </div>
            <div className="absolute inset-0 bg-gradient-to-br from-primary to-secondary rounded-2xl opacity-20 blur-lg scale-110"></div>
          </div>
        </div>

        {/* Main Heading */}
        <h1 className="text-5xl md:text-7xl font-heading font-bold text-foreground mb-6 leading-tight">
          <span className="bg-gradient-to-r from-primary via-secondary to-accent bg-clip-text text-transparent">
            GeForce Presence
          </span>
        </h1>

        {/* Tagline */}
        <p className="text-xl md:text-2xl text-text-secondary mb-4 max-w-3xl mx-auto leading-relaxed">
          Elevate your GeForce NOW gaming sessions with stylish Discord Rich Presence integration
        </p>

        {/* Subtitle */}
        <p className="text-lg text-text-secondary/80 mb-12 max-w-2xl mx-auto">
          Open-source application that automatically displays your current game with beautiful custom presence
        </p>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <Button
            variant="default"
            size="lg"
            iconName="Download"
            iconPosition="left"
            iconSize={20}
            className="glow-primary-hover micro-interact px-8 py-4 text-lg font-semibold"
          >
            Download on GitHub
          </Button>
          
          <Button
            variant="outline"
            size="lg"
            iconName="Eye"
            iconPosition="left"
            iconSize={20}
            className="micro-interact px-8 py-4 text-lg border-primary/30 hover:border-primary text-primary hover:bg-primary/10"
          >
            View Examples
          </Button>
          
          <Button
            variant="secondary"
            size="lg"
            iconName="Rocket"
            iconPosition="left"
            iconSize={20}
            className="micro-interact px-8 py-4 text-lg"
          >
            Get Started
          </Button>
        </div>

        {/* Stats */}
        <div className="flex flex-col sm:flex-row gap-8 justify-center items-center mt-16 pt-8 border-t border-border/30">
          <div className="text-center">
            <div className="text-2xl font-bold text-primary">1.2k+</div>
            <div className="text-sm text-text-secondary">GitHub Stars</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-secondary">50+</div>
            <div className="text-sm text-text-secondary">Supported Games</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-accent">10k+</div>
            <div className="text-sm text-text-secondary">Active Users</div>
          </div>
        </div>
      </div>

      {/* Scroll Indicator */}
      <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce">
        <Icon name="ChevronDown" size={24} color="var(--color-text-secondary)" />
      </div>
    </section>
  );
};

export default HeroSection;