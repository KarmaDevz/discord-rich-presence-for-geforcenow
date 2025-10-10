import React from 'react';
import Icon from '../../../components/AppIcon';
import Button from '../../../components/ui/Button';

const RepositorySection = () => {
  const repoStats = [
    {
      icon: "Star",
      label: "Stars",
      value: "1,247",
      color: "warning"
    },
    {
      icon: "GitFork",
      label: "Forks",
      value: "89",
      color: "primary"
    },
    {
      icon: "Eye",
      label: "Watchers",
      value: "156",
      color: "secondary"
    },
    {
      icon: "Download",
      label: "Downloads",
      value: "12.5k",
      color: "success"
    }
  ];

  const contributors = [
    {
      id: 1,
      name: "KarmaDevz",
      role: "Creator & Lead Developer",
      avatar: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop&crop=face",
      contributions: "245 commits"
    },
    {
      id: 2,
      name: "GameDev_Sarah",
      role: "UI/UX Designer",
      avatar: "https://images.unsplash.com/photo-1494790108755-2616b612b786?w=100&h=100&fit=crop&crop=face",
      contributions: "67 commits"
    },
    {
      id: 3,
      name: "CodeMaster_Alex",
      role: "Backend Developer",
      avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=face",
      contributions: "134 commits"
    },
    {
      id: 4,
      name: "TestingPro_Mike",
      role: "QA Engineer",
      avatar: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=100&h=100&fit=crop&crop=face",
      contributions: "89 commits"
    }
  ];

  const getStatColor = (color) => {
    const colorMap = {
      warning: "var(--color-warning)",
      primary: "var(--color-primary)",
      secondary: "var(--color-secondary)",
      success: "var(--color-success)"
    };
    return colorMap?.[color] || colorMap?.primary;
  };

  return (
    <section className="py-20 px-6 bg-background">
      <div className="max-w-6xl mx-auto">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-heading font-bold text-foreground mb-6">
            Open Source
            <span className="bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent"> Community</span>
          </h2>
          <p className="text-xl text-text-secondary max-w-3xl mx-auto leading-relaxed">
            Join thousands of developers and gamers contributing to the future of Discord Rich Presence
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
          {/* Repository Info */}
          <div className="space-y-8">
            {/* GitHub Card */}
            <div className="glass-card p-8 border-primary/20">
              <div className="flex items-center space-x-4 mb-6">
                <div className="w-16 h-16 bg-gradient-to-br from-surface to-card rounded-xl flex items-center justify-center border border-border/50">
                  <Icon name="Github" size={32} color="var(--color-foreground)" />
                </div>
                <div>
                  <h3 className="text-2xl font-heading font-semibold text-foreground">
                    GeForce-Presence
                  </h3>
                  <p className="text-text-secondary">
                    KarmaDevz/GeForce-Presence
                  </p>
                </div>
              </div>

              <p className="text-text-secondary leading-relaxed mb-6">
                A powerful Discord Rich Presence application specifically designed for GeForce NOW users. 
                Features automatic game detection, custom artwork, and seamless integration with your gaming sessions.
              </p>

              {/* Repository Stats */}
              <div className="grid grid-cols-2 gap-4 mb-8">
                {repoStats?.map((stat, index) => (
                  <div key={index} className="flex items-center space-x-3 p-3 bg-surface/30 rounded-lg border border-border/20">
                    <Icon 
                      name={stat?.icon} 
                      size={20} 
                      color={getStatColor(stat?.color)} 
                    />
                    <div>
                      <div className="text-lg font-semibold text-foreground">
                        {stat?.value}
                      </div>
                      <div className="text-sm text-text-secondary">
                        {stat?.label}
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Action Buttons */}
              <div className="flex flex-col sm:flex-row gap-4">
                <Button
                  variant="default"
                  iconName="Github"
                  iconPosition="left"
                  iconSize={18}
                  className="glow-primary-hover micro-interact flex-1"
                >
                  View Repository
                </Button>
                <Button
                  variant="outline"
                  iconName="Star"
                  iconPosition="left"
                  iconSize={18}
                  className="micro-interact border-warning/30 text-warning hover:bg-warning/10"
                >
                  Star on GitHub
                </Button>
              </div>
            </div>

            {/* License & Tech Stack */}
            <div className="glass-card p-6">
              <h4 className="text-lg font-semibold text-foreground mb-4">
                Technical Details
              </h4>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-text-secondary">License</span>
                  <span className="text-success font-mono">MIT</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-text-secondary">Language</span>
                  <span className="text-primary font-mono">Python</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-text-secondary">Platform</span>
                  <span className="text-secondary font-mono">Windows</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-text-secondary">Last Updated</span>
                  <span className="text-accent font-mono">2 days ago</span>
                </div>
              </div>
            </div>
          </div>

          {/* Contributors & Community */}
          <div className="space-y-8">
            {/* Contributors */}
            <div className="glass-card p-8">
              <h3 className="text-2xl font-heading font-semibold text-foreground mb-6">
                Top Contributors
              </h3>
              <div className="space-y-4">
                {contributors?.map((contributor) => (
                  <div key={contributor?.id} className="flex items-center space-x-4 p-4 bg-surface/30 rounded-lg border border-border/20 hover:border-primary/30 transition-colors duration-300">
                    <div className="w-12 h-12 rounded-full overflow-hidden">
                      <img 
                        src={contributor?.avatar} 
                        alt={contributor?.name}
                        className="w-full h-full object-cover"
                      />
                    </div>
                    <div className="flex-1">
                      <div className="text-foreground font-semibold">
                        {contributor?.name}
                      </div>
                      <div className="text-text-secondary text-sm">
                        {contributor?.role}
                      </div>
                    </div>
                    <div className="text-primary text-sm font-mono">
                      {contributor?.contributions}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Community Stats */}
            <div className="glass-card p-8">
              <h3 className="text-2xl font-heading font-semibold text-foreground mb-6">
                Community Impact
              </h3>
              <div className="grid grid-cols-2 gap-6">
                <div className="text-center">
                  <div className="text-3xl font-bold text-primary mb-2">15+</div>
                  <div className="text-sm text-text-secondary">Contributors</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-secondary mb-2">89</div>
                  <div className="text-sm text-text-secondary">Issues Resolved</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-accent mb-2">156</div>
                  <div className="text-sm text-text-secondary">Pull Requests</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-success mb-2">24</div>
                  <div className="text-sm text-text-secondary">Releases</div>
                </div>
              </div>
            </div>

            {/* Contribution CTA */}
            <div className="glass-card p-8 bg-gradient-to-br from-primary/10 to-secondary/10 border-primary/20">
              <div className="text-center">
                <Icon name="Heart" size={32} color="var(--color-primary)" className="mx-auto mb-4" />
                <h4 className="text-xl font-semibold text-foreground mb-4">
                  Want to Contribute?
                </h4>
                <p className="text-text-secondary mb-6">
                  Join our community of developers and help make GeForce Presence even better!
                </p>
                <div className="flex flex-col sm:flex-row gap-3">
                  <Button
                    variant="default"
                    iconName="GitPullRequest"
                    iconPosition="left"
                    iconSize={16}
                    className="micro-interact"
                  >
                    Submit PR
                  </Button>
                  <Button
                    variant="outline"
                    iconName="MessageSquare"
                    iconPosition="left"
                    iconSize={16}
                    className="micro-interact border-secondary/30 text-secondary hover:bg-secondary/10"
                  >
                    Join Discord
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default RepositorySection;