import React from 'react';
import Icon from '../../../components/AppIcon';

const UsageGuideSection = () => {
  const steps = [
    {
      id: 1,
      icon: "Download",
      title: "Download",
      description: "Get the latest release from our GitHub repository and extract the files to your preferred directory.",
      details: [
        "Visit the GitHub releases page",
        "Download the latest version",
        "Extract to your desired folder"
      ],
      color: "primary"
    },
    {
      id: 2,
      icon: "Settings",
      title: "Configure",
      description: "Run the configuration wizard to set up your preferences and customize your Discord Rich Presence display.",
      details: [
        "Launch the configuration tool",
        "Select your preferred games",
        "Customize presence settings"
      ],
      color: "secondary"
    },
    {
      id: 3,
      icon: "Play",
      title: "Run",
      description: "Start the application and begin gaming on GeForce NOW. Your Discord status will update automatically.",
      details: [
        "Launch GeForce Presence",
        "Start your GeForce NOW session",
        "Enjoy automatic status updates"
      ],
      color: "accent"
    }
  ];

  const getColorClasses = (color) => {
    const colorMap = {
      primary: "bg-primary text-background",
      secondary: "bg-secondary text-background",
      accent: "bg-accent text-background"
    };
    return colorMap?.[color] || colorMap?.primary;
  };

  const getBorderColor = (color) => {
    const colorMap = {
      primary: "border-primary/30",
      secondary: "border-secondary/30",
      accent: "border-accent/30"
    };
    return colorMap?.[color] || colorMap?.primary;
  };

  return (
    <section id="installation" className="py-20 px-6 bg-gradient-to-b from-background to-surface/30">
      <div className="max-w-6xl mx-auto">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-heading font-bold text-foreground mb-6">
            Get Started in
            <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent"> 3 Simple Steps</span>
          </h2>
          <p className="text-xl text-text-secondary max-w-3xl mx-auto leading-relaxed">
            Setting up GeForce Presence is quick and straightforward. Follow these steps to enhance your gaming presence.
          </p>
        </div>

        {/* Steps Container */}
        <div className="relative">
          {/* Connection Line */}
          <div className="hidden lg:block absolute top-24 left-1/2 transform -translate-x-1/2 w-full max-w-4xl">
            <div className="flex justify-between items-center">
              <div className="w-1/3 h-0.5 bg-gradient-to-r from-primary to-secondary opacity-30"></div>
              <div className="w-1/3 h-0.5 bg-gradient-to-r from-secondary to-accent opacity-30"></div>
            </div>
          </div>

          {/* Steps Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 lg:gap-12">
            {steps?.map((step, index) => (
              <div key={step?.id} className="relative">
                {/* Step Card */}
                <div className={`glass-card p-8 hover:scale-105 transition-all duration-300 micro-interact border ${getBorderColor(step?.color)}`}>
                  {/* Step Number */}
                  <div className="flex items-center justify-between mb-6">
                    <div className={`w-12 h-12 rounded-full ${getColorClasses(step?.color)} flex items-center justify-center font-bold text-lg`}>
                      {step?.id}
                    </div>
                    <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-surface to-card flex items-center justify-center border border-border/50">
                      <Icon 
                        name={step?.icon} 
                        size={28} 
                        color={`var(--color-${step?.color})`} 
                        strokeWidth={2}
                      />
                    </div>
                  </div>

                  {/* Step Content */}
                  <h3 className="text-2xl font-heading font-semibold text-foreground mb-4">
                    {step?.title}
                  </h3>
                  <p className="text-text-secondary leading-relaxed mb-6">
                    {step?.description}
                  </p>

                  {/* Step Details */}
                  <ul className="space-y-3">
                    {step?.details?.map((detail, detailIndex) => (
                      <li key={detailIndex} className="flex items-center text-sm text-text-secondary">
                        <Icon name="Check" size={16} color={`var(--color-${step?.color})`} className="mr-3 flex-shrink-0" />
                        {detail}
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Mobile Connection Arrow */}
                {index < steps?.length - 1 && (
                  <div className="lg:hidden flex justify-center my-6">
                    <Icon name="ArrowDown" size={24} color="var(--color-text-secondary)" />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Additional Info */}
        <div className="mt-16 text-center">
          <div className="glass-card p-8 max-w-4xl mx-auto">
            <div className="flex items-center justify-center mb-4">
              <Icon name="Info" size={24} color="var(--color-primary)" className="mr-3" />
              <h3 className="text-xl font-heading font-semibold text-foreground">
                System Requirements
              </h3>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-sm text-text-secondary">
              <div className="flex items-center justify-center">
                <Icon name="Monitor" size={18} color="var(--color-accent)" className="mr-2" />
                Windows 10/11
              </div>
              <div className="flex items-center justify-center">
                <Icon name="Wifi" size={18} color="var(--color-accent)" className="mr-2" />
                Internet Connection
              </div>
              <div className="flex items-center justify-center">
                <Icon name="MessageSquare" size={18} color="var(--color-accent)" className="mr-2" />
                Discord Desktop App
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default UsageGuideSection;