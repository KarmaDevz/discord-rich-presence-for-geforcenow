from pypresence import Presence
import time

client_id = "1400696164055121973"
rpc = Presence(client_id)
rpc.connect()

rpc.update(
    details="En la sala del sueño",
    state="Lobby - 1 jugador",
    large_image="outlast_trials",
    small_image="steam",
    party_id="ef0c3241-d2e2-b20c-5221-dfffab77b970",
    party_size=[1, 4],
    join="joinplayer=ef0c3241-d2e2-b20c-5221-dfffab77b970"
)

print("🩸 Presence simulando 'The Outlast Trials' con botón de 'Ask to Join'")
while True:
    time.sleep(15)
