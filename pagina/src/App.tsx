import './App.css';
import DarkVeil from './components/DarkVeil';
import BlurText from './components/BlurText';
import ProfileCard from './components/ProfileCard'
import InfiniteScroll from './components/InfiniteScroll';

function App() {
  const handleAnimationComplete = () => {
  console.log('Animation completed!');
};
const items = [
  { content: <img src="https://media.discordapp.net/attachments/747361700239376385/1423471719452119060/image.png?ex=68e06ed8&is=68df1d58&hm=de5661c9e316e30663653b859e00cbe50015039f006a765c664f9781ba38c423&=&format=webp&quality=lossless" alt="Icon 1" style={{ width: '50px', height: '50px' }} /> },
  { content: <p>Paragraph Item 2</p> },
  { content: "Text Item 3" },
  { content: <p>Paragraph Item 4</p> },
  { content: "Text Item 5" },
  { content: <p>Paragraph Item 6</p> },
  { content: "Text Item 7" },
  { content: <p>Paragraph Item 8</p> },
  { content: "Text Item 9" },
  { content: <p>Paragraph Item 10</p> },
  { content: "Text Item 11" },
  { content: <p>Paragraph Item 12</p> },
  { content: "Text Item 13" },
  { content: <p>Paragraph Item 14</p> },
];


  return (
    <>
      

      <div style={{ width: '100vw', height: '100vh', position: 'relative', display: 'inherit' }}>
        <DarkVeil />
        <div
          
        >
          <BlurText
            text="GeForce NOW + Discord Presence"
            delay={150}
            animateBy="letters"
            direction="top"
            onAnimationComplete={handleAnimationComplete}
            className="main-title"
          />

          <div className="contenedor">
            <div className="izquierdo">
              <ProfileCard
                avatarUrl="https://images.icon-icons.com/3053/PNG/512/geforce_now_macos_bigsur_icon_190147.png"
                iconUrl="https://static.vecteezy.com/system/resources/thumbnails/023/741/164/small_2x/discord-logo-icon-social-media-icon-free-png.png"
                showBehindGradient={true}
                className=""
                enableTilt={true}
                enableMobileTilt={false}
                mobileTiltSensitivity={5}
                name="Camilo García"
                title="Software Engineer"
                handle="camilo.magnus"
                status="Online"
                contactText="Contact"
                showUserInfo={true}
                onContactClick={() =>
                  window.open(
                    "https://github.com/KarmaDevz/discord-rich-presence-for-geforcenow",
                    "_blank"
                  )
                }
              />
            </div>

            <div className="derecho" style={{ height: "500px", position: "static", overflow: "hidden" ,color: 'white'}}>
              <InfiniteScroll
                items={items}
                isTilted={true}
                tiltDirection="left"
                autoplay={true}
                autoplaySpeed={1}
                autoplayDirection="down"
                pauseOnHover={true}
              />
            </div>
          </div>
        </div>
      </div>

    </>
  );
}

export default App;
