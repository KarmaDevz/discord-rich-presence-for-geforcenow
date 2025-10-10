import React from 'react';
import Icon from '../../../components/AppIcon';

const Footer = () => {
  const currentYear = new Date()?.getFullYear();

  const socialLinks = [
    {
      name: "GitHub",
      icon: "Github",
      url: "https://github.com/karmadevz/geforce-presence",
      color: "var(--color-foreground)"
    },
    {
      name: "Discord",
      icon: "MessageSquare",
      url: "https://discord.gg/karmadevz",
      color: "var(--color-primary)"
    },
    {
      name: "Email",
      icon: "Mail",
      url: "mailto:contact@karmadevz.com",
      color: "var(--color-secondary)"
    }
  ];

  const quickLinks = [
    { name: "Features", href: "#features" },
    { name: "Installation", href: "#installation" },
    { name: "Examples", href: "#examples" },
    { name: "FAQ", href: "#faq" }
  ];

  const resourceLinks = [
    { name: "Documentation", href: "#documentation" },
    { name: "GitHub Repository", href: "https://github.com/karmadevz/geforce-presence" },
    { name: "Release Notes", href: "#releases" },
    { name: "Contributing", href: "#contributing" }
  ];

  return (
    <footer className="bg-gradient-to-t from-surface to-background border-t border-border/30">
      <div className="max-w-7xl mx-auto px-6 py-16">
        {/* Main Footer Content */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12 mb-12">
          {/* Brand Section */}
          <div className="lg:col-span-2">
            <div className="flex items-center space-x-3 mb-6">
              <div className="relative">
                <div className="w-12 h-12 bg-gradient-to-br from-primary to-secondary rounded-xl flex items-center justify-center glow-primary">
                  <Icon name="Gamepad2" size={24} color="var(--color-background)" strokeWidth={2.5} />
                </div>
                <div className="absolute inset-0 bg-gradient-to-br from-primary to-secondary rounded-xl opacity-20 blur-sm"></div>
              </div>
              <div>
                <div className="text-2xl font-heading font-bold text-foreground">
                  GeForce Presence
                </div>
                <div className="text-sm font-mono text-text-secondary">
                  by KarmaDevz
                </div>
              </div>
            </div>
            <p className="text-text-secondary leading-relaxed mb-6 max-w-md">
              Enhance your GeForce NOW gaming sessions with beautiful Discord Rich Presence integration. 
              Open-source, lightweight, and designed specifically for gamers.
            </p>
            
            {/* Social Links */}
            <div className="flex space-x-4">
              {socialLinks?.map((social) => (
                <a
                  key={social?.name}
                  href={social?.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-10 h-10 bg-surface/50 hover:bg-surface border border-border/30 hover:border-primary/30 rounded-lg flex items-center justify-center transition-all duration-300 micro-interact group"
                  aria-label={social?.name}
                >
                  <Icon 
                    name={social?.icon} 
                    size={18} 
                    color="var(--color-text-secondary)"
                    className="group-hover:text-primary transition-colors duration-300"
                  />
                </a>
              ))}
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="text-lg font-heading font-semibold text-foreground mb-6">
              Quick Links
            </h3>
            <ul className="space-y-3">
              {quickLinks?.map((link) => (
                <li key={link?.name}>
                  <a
                    href={link?.href}
                    className="text-text-secondary hover:text-primary transition-colors duration-300 flex items-center space-x-2 group"
                  >
                    <Icon 
                      name="ArrowRight" 
                      size={14} 
                      className="opacity-0 group-hover:opacity-100 transition-opacity duration-300" 
                    />
                    <span>{link?.name}</span>
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h3 className="text-lg font-heading font-semibold text-foreground mb-6">
              Resources
            </h3>
            <ul className="space-y-3">
              {resourceLinks?.map((link) => (
                <li key={link?.name}>
                  <a
                    href={link?.href}
                    target={link?.href?.startsWith('http') ? '_blank' : '_self'}
                    rel={link?.href?.startsWith('http') ? 'noopener noreferrer' : ''}
                    className="text-text-secondary hover:text-primary transition-colors duration-300 flex items-center space-x-2 group"
                  >
                    <Icon 
                      name="ArrowRight" 
                      size={14} 
                      className="opacity-0 group-hover:opacity-100 transition-opacity duration-300" 
                    />
                    <span>{link?.name}</span>
                  </a>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Stats Section */}
        <div className="glass-card p-8 mb-12">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-2xl font-bold text-primary mb-1">1.2k+</div>
              <div className="text-sm text-text-secondary">GitHub Stars</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-secondary mb-1">50+</div>
              <div className="text-sm text-text-secondary">Games Supported</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-accent mb-1">10k+</div>
              <div className="text-sm text-text-secondary">Downloads</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-success mb-1">24/7</div>
              <div className="text-sm text-text-secondary">Community Support</div>
            </div>
          </div>
        </div>

        {/* Bottom Section */}
        <div className="flex flex-col md:flex-row justify-between items-center pt-8 border-t border-border/30">
          <div className="flex flex-col md:flex-row items-center space-y-2 md:space-y-0 md:space-x-6 text-sm text-text-secondary">
            <div className="flex items-center space-x-2">
              <Icon name="Copyright" size={16} />
              <span>{currentYear} KarmaDevz. All rights reserved.</span>
            </div>
            <div className="flex items-center space-x-4">
              <a href="#privacy" className="hover:text-primary transition-colors duration-300">
                Privacy Policy
              </a>
              <span className="text-border">•</span>
              <a href="#terms" className="hover:text-primary transition-colors duration-300">
                Terms of Service
              </a>
              <span className="text-border">•</span>
              <a href="#license" className="hover:text-primary transition-colors duration-300">
                MIT License
              </a>
            </div>
          </div>

          <div className="flex items-center space-x-2 mt-4 md:mt-0 text-sm text-text-secondary">
            <span>Made with</span>
            <Icon name="Heart" size={16} color="var(--color-error)" className="animate-pulse" />
            <span>for the gaming community</span>
          </div>
        </div>

        {/* Version Info */}
        <div className="text-center mt-8 pt-6 border-t border-border/20">
          <div className="inline-flex items-center space-x-2 px-4 py-2 bg-surface/30 rounded-full border border-border/30">
            <Icon name="Zap" size={16} color="var(--color-primary)" />
            <span className="text-sm font-mono text-text-secondary">
              GeForce Presence v2.1.0
            </span>
            <div className="w-2 h-2 bg-success rounded-full animate-pulse"></div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;