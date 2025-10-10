import React from 'react';
import Icon from '../../../components/AppIcon';

const FeaturesSection = () => {
  const features = [
    {
      id: 1,
      icon: "Zap",
      title: "Dynamic Rich Presence",
      description: "Automatically detects and displays your current GeForce NOW game with real-time status updates and beautiful custom artwork.",
      color: "primary"
    },
    {
      id: 2,
      icon: "Gamepad2",
      title: "Multi-Game Support",
      description: "Supports 50+ popular games with automatic client_id switching and game-specific presence configurations.",
      color: "secondary"
    },
    {
      id: 3,
      icon: "Globe",
      title: "Translated Text Support",
      description: "Localized presence text in multiple languages to match your Discord client and gaming preferences.",
      color: "accent"
    },
    {
      id: 4,
      icon: "Settings",
      title: "Easy Configuration",
      description: "Simple setup process with intuitive configuration options and automatic game detection capabilities.",
      color: "warning"
    },
    {
      id: 5,
      icon: "Shield",
      title: "Open Source",
      description: "Fully transparent codebase hosted on GitHub with active community contributions and regular updates.",
      color: "success"
    },
    {
      id: 6,
      icon: "Cpu",
      title: "Lightweight Performance",
      description: "Minimal system resource usage with efficient background processing that won\'t impact your gaming performance.",
      color: "primary"
    }
  ];

  const getColorClasses = (color) => {
    const colorMap = {
      primary: "from-primary/20 to-primary/5 border-primary/30",
      secondary: "from-secondary/20 to-secondary/5 border-secondary/30",
      accent: "from-accent/20 to-accent/5 border-accent/30",
      warning: "from-warning/20 to-warning/5 border-warning/30",
      success: "from-success/20 to-success/5 border-success/30"
    };
    return colorMap?.[color] || colorMap?.primary;
  };

  const getIconColor = (color) => {
    const colorMap = {
      primary: "var(--color-primary)",
      secondary: "var(--color-secondary)",
      accent: "var(--color-accent)",
      warning: "var(--color-warning)",
      success: "var(--color-success)"
    };
    return colorMap?.[color] || colorMap?.primary;
  };

  return (
    <section id="features" className="py-20 px-6 bg-background">
      <div className="max-w-7xl mx-auto">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-heading font-bold text-foreground mb-6">
            Powerful Features for
            <span className="bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent"> Gamers</span>
          </h2>
          <p className="text-xl text-text-secondary max-w-3xl mx-auto leading-relaxed">
            Everything you need to showcase your gaming sessions with style and precision
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features?.map((feature) => (
            <div
              key={feature?.id}
              className={`glass-card p-8 hover:scale-105 transition-all duration-300 micro-interact bg-gradient-to-br ${getColorClasses(feature?.color)}`}
            >
              {/* Feature Icon */}
              <div className="mb-6">
                <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-surface to-card flex items-center justify-center border border-border/50">
                  <Icon 
                    name={feature?.icon} 
                    size={28} 
                    color={getIconColor(feature?.color)} 
                    strokeWidth={2}
                  />
                </div>
              </div>

              {/* Feature Content */}
              <h3 className="text-xl font-heading font-semibold text-foreground mb-4">
                {feature?.title}
              </h3>
              <p className="text-text-secondary leading-relaxed">
                {feature?.description}
              </p>

              {/* Hover Effect */}
              <div className="mt-6 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <Icon name="ArrowRight" size={20} color="var(--color-primary)" />
              </div>
            </div>
          ))}
        </div>

        {/* Bottom CTA */}
        <div className="text-center mt-16">
          <p className="text-lg text-text-secondary mb-6">
            Ready to enhance your gaming presence?
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="px-8 py-3 bg-gradient-to-r from-primary to-secondary text-background font-semibold rounded-lg glow-primary-hover micro-interact">
              Explore All Features
            </button>
            <button className="px-8 py-3 border border-primary/30 text-primary hover:bg-primary/10 font-semibold rounded-lg micro-interact">
              View Documentation
            </button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default FeaturesSection;