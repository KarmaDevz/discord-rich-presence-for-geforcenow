import React, { useEffect } from 'react';
import { Helmet } from 'react-helmet';
import Header from '../../components/ui/Header';
import HeroSection from './components/HeroSection';
import FeaturesSection from './components/FeaturesSection';
import UsageGuideSection from './components/UsageGuideSection';
import ExamplesSection from './components/ExamplesSection';
import RepositorySection from './components/RepositorySection';
import FAQSection from './components/FAQSection';
import Footer from './components/Footer';

const MarketingLandingPage = () => {
  useEffect(() => {
    // Smooth scroll behavior for anchor links
    const handleSmoothScroll = (e) => {
      const target = e?.target?.closest('a[href^="#"]');
      if (target) {
        e?.preventDefault();
        const targetId = target?.getAttribute('href')?.substring(1);
        const targetElement = document.getElementById(targetId);
        if (targetElement) {
          targetElement?.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
          });
        }
      }
    };

    document.addEventListener('click', handleSmoothScroll);
    return () => document.removeEventListener('click', handleSmoothScroll);
  }, []);

  return (
    <>
      <Helmet>
        <title>GeForce Presence - Discord Rich Presence for GeForce NOW | KarmaDevz</title>
        <meta 
          name="description" 
          content="Enhance your GeForce NOW gaming sessions with beautiful Discord Rich Presence integration. Open-source application supporting 50+ games with automatic detection and custom artwork." 
        />
        <meta 
          name="keywords" 
          content="GeForce NOW, Discord Rich Presence, Gaming, Open Source, KarmaDevz, PC Gaming, Cloud Gaming" 
        />
        <meta name="author" content="KarmaDevz" />
        <meta property="og:title" content="GeForce Presence - Discord Rich Presence for GeForce NOW" />
        <meta 
          property="og:description" 
          content="Elevate your GeForce NOW gaming sessions with stylish Discord Rich Presence integration. Free, open-source, and designed for gamers." 
        />
        <meta property="og:type" content="website" />
        <meta property="og:url" content="https://karmadevz.com/geforce-presence" />
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content="GeForce Presence - Discord Rich Presence for GeForce NOW" />
        <meta 
          name="twitter:description" 
          content="Enhance your gaming presence with automatic game detection and beautiful custom artwork." 
        />
        <link rel="canonical" href="https://karmadevz.com/geforce-presence" />
      </Helmet>

      <div className="min-h-screen bg-background text-foreground">
        {/* Header */}
        <Header />

        {/* Main Content */}
        <main className="pt-16">
          {/* Hero Section */}
          <HeroSection />

          {/* Features Section */}
          <FeaturesSection />

          {/* Usage Guide Section */}
          <UsageGuideSection />

          {/* Examples Section */}
          <ExamplesSection />

          {/* Repository Section */}
          <RepositorySection />

          {/* FAQ Section */}
          <FAQSection />
        </main>

        {/* Footer */}
        <Footer />
      </div>
    </>
  );
};

export default MarketingLandingPage;