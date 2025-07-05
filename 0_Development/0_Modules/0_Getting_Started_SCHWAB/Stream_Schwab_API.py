import schwabdev
import time

client = schwabdev.Client(app_key= "XAuRzDiRG9z1jYnz8gkwcKZa6k3HHAVv", app_secret= "pHToyhfrHvtwrHMA")
# Error with client.update_tokens_auto(), could be missing the capital "C" or outdated. 
#client.update_tokens_auto()

print(client.quote("AMD").json())



# client.stream.start() OR attach client.stream to a variable to "streamer" or "AAPL_197_Strike" --> AAPL_197_Strike.start()
streamer = client.stream


# Make a response handler to visualize and store the streamed data
def response_handler(response):
    print(response)


streamer.start(response_handler)
# streamer.send() is missing required positional argument 'requests' 
#streamer.send()

# OR ask for the specified fields you want streamed?
# streamer.send(streamer.level_one_equities("AMD", "0,1,2,3,4,5"))

# YOU can add commands (ADD, SUBS, UNSUBS, VIEW, )
# Outside of level_one_equities, you can subscribe to options, futures, forex, etc. --> check all of the 13 or 14 streams you can subscribe to 
# streamer.send(streamer.elevel_one_equities("AMD", "0,1,2,3,4,5", command="ADD"))

time.sleep(10)

streamer.stop()