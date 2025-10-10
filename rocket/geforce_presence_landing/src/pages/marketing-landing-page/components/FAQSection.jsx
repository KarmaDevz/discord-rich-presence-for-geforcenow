import React, { useState } from 'react';
import Icon from '../../../components/AppIcon';

const FAQSection = () => {
  const [openFAQ, setOpenFAQ] = useState(null);

  const faqs = [
    {
      id: 1,
      question: "Does GeForce Presence support all games on GeForce NOW?",
      answer: `GeForce Presence supports 50+ of the most popular games on GeForce NOW, including Cyberpunk 2077, Fortnite, Apex Legends, and many more. The application automatically detects supported games and displays appropriate Rich Presence information.\n\nFor unsupported games, the application will show a generic "Playing on GeForce NOW" status. We're constantly adding support for new games based on community requests.`
    },
    {
      id: 2,
      question: "Do I need GeForce NOW to use this application?",
      answer: `Yes, GeForce Presence is specifically designed for GeForce NOW cloud gaming service. The application works by detecting when you're streaming games through GeForce NOW and automatically updating your Discord status accordingly.\n\nIf you're not using GeForce NOW, this application won't be able to detect your games or provide Rich Presence functionality.`
    },
    {
      id: 3,
      question: "How do I add support for new games?",
      answer: `Adding support for new games is easy! You can contribute to the project by:\n\n1. Creating a GitHub issue with the game name and details\n2. Submitting a pull request with the game configuration\n3. Joining our Discord community to request new games\n\nOur community actively maintains and updates the game database, so new popular games are added regularly.`
    },
    {
      id: 4,
      question: "Is GeForce Presence safe to use?",
      answer: `Absolutely! GeForce Presence is completely open-source, which means you can review the entire codebase on GitHub. The application:\n\n• Only reads game information from GeForce NOW\n• Doesn't collect or store personal data\n• Uses official Discord Rich Presence APIs\n• Has been reviewed by thousands of users\n\nBeing open-source ensures complete transparency and security.`
    },
    {
      id: 5,
      question: "Can I customize the Rich Presence display?",
      answer: `Yes! GeForce Presence offers several customization options:\n\n• Custom status messages and descriptions\n• Personalized game artwork and icons\n• Configurable timestamp display\n• Language localization support\n• Party size and multiplayer information\n\nYou can modify these settings through the configuration file or the built-in settings interface.`
    },
    {
      id: 6,
      question: "What are the system requirements?",
      answer: `GeForce Presence has minimal system requirements:\n\n• Windows 10 or Windows 11\n• Discord Desktop Application\n• Active GeForce NOW subscription\n• Internet connection for Rich Presence updates\n• ~50MB of free disk space\n\nThe application runs efficiently in the background with minimal resource usage.`
    }
  ];

  const toggleFAQ = (id) => {
    setOpenFAQ(openFAQ === id ? null : id);
  };

  return (
    <section className="py-20 px-6 bg-gradient-to-b from-background to-surface/30">
      <div className="max-w-4xl mx-auto">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-heading font-bold text-foreground mb-6">
            Frequently Asked
            <span className="bg-gradient-to-r from-secondary to-accent bg-clip-text text-transparent"> Questions</span>
          </h2>
          <p className="text-xl text-text-secondary max-w-3xl mx-auto leading-relaxed">
            Get answers to common questions about GeForce Presence setup, compatibility, and features
          </p>
        </div>

        {/* FAQ Items */}
        <div className="space-y-4">
          {faqs?.map((faq) => (
            <div
              key={faq?.id}
              className="glass-card border border-border/30 hover:border-primary/30 transition-all duration-300"
            >
              {/* Question */}
              <button
                onClick={() => toggleFAQ(faq?.id)}
                className="w-full p-6 text-left flex items-center justify-between hover:bg-surface/20 transition-colors duration-300"
              >
                <h3 className="text-lg font-semibold text-foreground pr-4">
                  {faq?.question}
                </h3>
                <div className={`transform transition-transform duration-300 flex-shrink-0 ${
                  openFAQ === faq?.id ? 'rotate-180' : ''
                }`}>
                  <Icon 
                    name="ChevronDown" 
                    size={24} 
                    color="var(--color-primary)" 
                  />
                </div>
              </button>

              {/* Answer */}
              <div className={`progressive-disclosure ${openFAQ === faq?.id ? 'open' : ''}`}>
                <div className="px-6 pb-6">
                  <div className="border-t border-border/20 pt-4">
                    <div className="text-text-secondary leading-relaxed whitespace-pre-line">
                      {faq?.answer}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Additional Help */}
        <div className="mt-16 text-center">
          <div className="glass-card p-8 bg-gradient-to-br from-primary/5 to-secondary/5 border-primary/20">
            <div className="flex items-center justify-center mb-4">
              <Icon name="HelpCircle" size={32} color="var(--color-primary)" />
            </div>
            <h3 className="text-2xl font-heading font-semibold text-foreground mb-4">
              Still Have Questions?
            </h3>
            <p className="text-text-secondary mb-6 max-w-2xl mx-auto">
              Can't find what you're looking for? Our community is here to help! Join our Discord server or check out the documentation for more detailed information.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button className="px-6 py-3 bg-gradient-to-r from-primary to-secondary text-background font-semibold rounded-lg glow-primary-hover micro-interact flex items-center justify-center space-x-2">
                <Icon name="MessageSquare" size={18} />
                <span>Join Discord Community</span>
              </button>
              <button className="px-6 py-3 border border-primary/30 text-primary hover:bg-primary/10 font-semibold rounded-lg micro-interact flex items-center justify-center space-x-2">
                <Icon name="Book" size={18} />
                <span>Read Documentation</span>
              </button>
            </div>
          </div>
        </div>

        {/* Quick Links */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="glass-card p-6 text-center hover:scale-105 transition-transform duration-300">
            <Icon name="Download" size={24} color="var(--color-success)" className="mx-auto mb-3" />
            <h4 className="text-lg font-semibold text-foreground mb-2">Installation Guide</h4>
            <p className="text-sm text-text-secondary">Step-by-step setup instructions</p>
          </div>
          <div className="glass-card p-6 text-center hover:scale-105 transition-transform duration-300">
            <Icon name="Settings" size={24} color="var(--color-warning)" className="mx-auto mb-3" />
            <h4 className="text-lg font-semibold text-foreground mb-2">Configuration</h4>
            <p className="text-sm text-text-secondary">Customize your Rich Presence</p>
          </div>
          <div className="glass-card p-6 text-center hover:scale-105 transition-transform duration-300">
            <Icon name="Bug" size={24} color="var(--color-error)" className="mx-auto mb-3" />
            <h4 className="text-lg font-semibold text-foreground mb-2">Report Issues</h4>
            <p className="text-sm text-text-secondary">Found a bug? Let us know!</p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default FAQSection;