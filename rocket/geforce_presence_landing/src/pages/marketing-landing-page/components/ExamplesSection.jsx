import React, { useState } from 'react';
import Icon from '../../../components/AppIcon';
import Image from '../../../components/AppImage';

const ExamplesSection = () => {
  const [activeExample, setActiveExample] = useState(0);

  const examples = [
    {
      id: 1,
      game: "Cyberpunk 2077",
      status: "Exploring Night City",
      timestamp: "Started 2 hours ago",
      image: "https://images.unsplash.com/photo-1542751371-adc38448a05e?w=400&h=300&fit=crop",
      details: {
        largeText: "Cyberpunk 2077",
        smallText: "Level 25 Netrunner",
        state: "Exploring Night City",
        partySize: "1 of 1"
      }
    },
    {
      id: 2,
      game: "Fortnite",
      status: "Battle Royale",
      timestamp: "Started 45 minutes ago",
      image: "https://images.unsplash.com/photo-1560419015-7c427e8ae5ba?w=400&h=300&fit=crop",
      details: {
        largeText: "Fortnite",
        smallText: "Solo Match",
        state: "Battle Royale",
        partySize: "1 of 100"
      }
    },
    {
      id: 3,
      game: "Assassin\'s Creed Valhalla",
      status: "Raiding England",
      timestamp: "Started 1 hour ago",
      image: "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400&h=300&fit=crop",
      details: {
        largeText: "Assassin\'s Creed Valhalla",
        smallText: "Viking Warrior",
        state: "Raiding England",
        partySize: "Solo Campaign"
      }
    },
    {
      id: 4,
      game: "Apex Legends",
      status: "Ranked Match",
      timestamp: "Started 30 minutes ago",
      image: "https://images.unsplash.com/photo-1542751371-adc38448a05e?w=400&h=300&fit=crop",
      details: {
        largeText: "Apex Legends",
        smallText: "Diamond Rank",
        state: "Ranked Match",
        partySize: "3 of 3"
      }
    }
  ];

  return (
    <section className="py-20 px-6 bg-gradient-to-b from-surface/30 to-background">
      <div className="max-w-7xl mx-auto">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-heading font-bold text-foreground mb-6">
            See It in
            <span className="bg-gradient-to-r from-secondary to-accent bg-clip-text text-transparent"> Action</span>
          </h2>
          <p className="text-xl text-text-secondary max-w-3xl mx-auto leading-relaxed">
            Experience how GeForce Presence transforms your Discord status with beautiful, game-specific rich presence displays
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Game Selection */}
          <div className="space-y-4">
            <h3 className="text-2xl font-heading font-semibold text-foreground mb-6">
              Popular Games Supported
            </h3>
            {examples?.map((example, index) => (
              <div
                key={example?.id}
                onClick={() => setActiveExample(index)}
                className={`glass-card p-6 cursor-pointer transition-all duration-300 micro-interact ${
                  activeExample === index 
                    ? 'border-primary/50 bg-primary/5' :'border-border/30 hover:border-primary/30'
                }`}
              >
                <div className="flex items-center space-x-4">
                  <div className="w-16 h-16 rounded-lg overflow-hidden">
                    <Image 
                      src={example?.image} 
                      alt={example?.game}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div className="flex-1">
                    <h4 className="text-lg font-semibold text-foreground">
                      {example?.game}
                    </h4>
                    <p className="text-text-secondary text-sm">
                      {example?.status}
                    </p>
                    <p className="text-text-secondary/60 text-xs mt-1">
                      {example?.timestamp}
                    </p>
                  </div>
                  <div className={`w-3 h-3 rounded-full transition-colors duration-300 ${
                    activeExample === index ? 'bg-primary' : 'bg-border'
                  }`}></div>
                </div>
              </div>
            ))}
          </div>

          {/* Discord Rich Presence Preview */}
          <div className="flex justify-center">
            <div className="glass-card p-8 max-w-md w-full">
              <div className="flex items-center space-x-3 mb-6">
                <div className="w-8 h-8 bg-gradient-to-br from-primary to-secondary rounded-full flex items-center justify-center">
                  <Icon name="MessageSquare" size={16} color="var(--color-background)" />
                </div>
                <span className="text-lg font-semibold text-foreground">Discord Rich Presence</span>
              </div>

              {/* User Profile Section */}
              <div className="flex items-center space-x-4 mb-6">
                <div className="w-12 h-12 bg-gradient-to-br from-accent to-success rounded-full flex items-center justify-center">
                  <Icon name="User" size={20} color="var(--color-background)" />
                </div>
                <div>
                  <div className="text-foreground font-semibold">GamerPro2024</div>
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 bg-success rounded-full"></div>
                    <span className="text-sm text-text-secondary">Online</span>
                  </div>
                </div>
              </div>

              {/* Rich Presence Card */}
              <div className="bg-surface/50 rounded-lg p-4 border border-border/30">
                <div className="flex items-start space-x-4">
                  <div className="w-16 h-16 rounded-lg overflow-hidden flex-shrink-0">
                    <Image 
                      src={examples?.[activeExample]?.image} 
                      alt={examples?.[activeExample]?.game}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-foreground font-semibold text-sm mb-1">
                      {examples?.[activeExample]?.details?.largeText}
                    </div>
                    <div className="text-text-secondary text-xs mb-2">
                      {examples?.[activeExample]?.details?.state}
                    </div>
                    <div className="text-text-secondary/80 text-xs">
                      {examples?.[activeExample]?.details?.smallText}
                    </div>
                    <div className="text-text-secondary/60 text-xs mt-2">
                      {examples?.[activeExample]?.timestamp}
                    </div>
                  </div>
                </div>
                
                {/* Party Info */}
                <div className="flex items-center justify-between mt-4 pt-3 border-t border-border/20">
                  <div className="text-xs text-text-secondary">
                    Party: {examples?.[activeExample]?.details?.partySize}
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-success rounded-full animate-pulse"></div>
                    <span className="text-xs text-success">Live</span>
                  </div>
                </div>
              </div>

              {/* Features List */}
              <div className="mt-6 space-y-3">
                <div className="flex items-center space-x-3 text-sm text-text-secondary">
                  <Icon name="Check" size={16} color="var(--color-success)" />
                  <span>Automatic game detection</span>
                </div>
                <div className="flex items-center space-x-3 text-sm text-text-secondary">
                  <Icon name="Check" size={16} color="var(--color-success)" />
                  <span>Real-time status updates</span>
                </div>
                <div className="flex items-center space-x-3 text-sm text-text-secondary">
                  <Icon name="Check" size={16} color="var(--color-success)" />
                  <span>Custom artwork & branding</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Stats */}
        <div className="mt-16 text-center">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="text-3xl font-bold text-primary mb-2">50+</div>
              <div className="text-sm text-text-secondary">Games Supported</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-secondary mb-2">24/7</div>
              <div className="text-sm text-text-secondary">Auto Detection</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-accent mb-2">0ms</div>
              <div className="text-sm text-text-secondary">Gaming Latency</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-success mb-2">100%</div>
              <div className="text-sm text-text-secondary">Free & Open</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default ExamplesSection;