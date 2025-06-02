# Knowledge Dump
Got these from https://new.crichd.tv/, go on to any of the channel pages and it would redirect to one of these(inside an embed page, probably they want people to also use their source so it might help in their p2p network)

https://crichdplayer.com/willow-cricket-live-stream-play-01
https://crichdplayer.com/star-sports-hindi-live-stream-play-01
https://crichdplayer.com/star-sports-1-live-stream-play-01
https://crichdplayer.com/sky-sports-cricket-live-stream-me-1

On each of these channel pages, we look for a php url, that php page is how we get the channel id's

i.e on https://crichdplayer.com/willow-cricket-live-stream-play-01
we find
```
<script>
embeds = new Array();
titles = new Array();
embeds[0] = '<iframe src="//stream.crichd.sc/update/willowcricket.php" width="100%" height="500px" marginheight="0" marginwidth="0" scrolling="no" frameborder="0" allowfullscreen  allow="encrypted-media"></iframe>'; titles[0] = 'Willow Cricket HD'; 
```

then once we fetch the contents https://stream.crichd.sc/update/willowcricket.php

in the response snippet we see
```
<script>fid="willowusa"; v_width="100%"; v_height="100%";</script><script type="text/javascript" src="//apex2nova.com/premium.js"></script>
```

Next we can look into the https://apex2nova.com/premium.js
```
// JScript File
var isMobile = {
    Android: function() {
        return navigator.userAgent.match(/Android/i);
    },
    BlackBerry: function() {
        return navigator.userAgent.match(/BlackBerry/i);
    },
    iOS: function() {
        return navigator.userAgent.match(/iPhone|iPad|iPod/i);
    },
    Opera: function() {
        return navigator.userAgent.match(/Opera Mini/i);
    },
    Windows: function() {
        return navigator.userAgent.match(/IEMobile/i);
    },
    MacOSX: function() {
        return navigator.userAgent.match(/Macintosh/i);
    },	
    any: function() {
        return (isMobile.Android() || isMobile.BlackBerry() || isMobile.iOS() || isMobile.Opera() || isMobile.Windows());
    }
};
var embedded = "mobile";
if (!isMobile.any()){
        embedded = "desktop";
}

if(v_height == "100%"){
    PlaySize = 'style="overflow:hidden;height:100%;width:100%"';
}
else{
    PlaySize = '';
}
document.write('<ifr'+'ame src="https://apex2nova.com/premium.php?player='+ embedded +'&live='+ fid +'" '+PlaySize +' width='+ v_width +' height=' + v_height + ' scrolling="no" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></ifr'+'ame>') ;
/**/
```

This will allow us to create the url to fetch the final page that contains the m3u8 url
The final URL  would be 
https://apex2nova.com/premium.php?player=desktop&live=willowusa

This page contains obfuscated javascript, that will be used to generate the m3u8 url and load it on the player
i.e for the url above we can get the contents and then start with getting the inline js, it'll look something like this

```
    <script type="text/javascript">
        var SuryngresaeAbiaerrtUl = [""];
        var SrrynursiaAetgrUeleab = [""];
        var gAterraSslrUbnauyiree = [""];
        var AseebrriurSrtlgUneaay = [""];
        var ruerrtleyiUAbeagSsran = [""];
        var rUurgAraeyebesatrilnS = [""];
        var lSearAaeUsetbirrnuygr = [""];
        var UlgtrSryAsrnabreiueea = [""];
        var lenreariUaAegSrytsurb = [""];
        var gertuarnyerlbsAiSrUea = [""];
        var erelAUiutagarsynSrebr = [""];
        var errgabreSaeriUtyunlAs = [""];
        var ruUensbaiareSrtlArgey = [""];
        var suaireenablgtyArUrSar = [""];
        var ASaaurenyerUblgiesrtr = [""];
        var neAaugtaeysrrbrUirelS = [""];
        var eelasrUugiybAranSrrte = [""];
        var asrngebutAreiaelrSrUy = [""];
        var yUbStaleinsrrgaeeuArr = [""];
        var rsAregynutbUeaSreirla = [""];
        var buSargnraerlUisetryAe = [""];
        var rgyaAbrlaUirsSrunetee = [""];
        var eurStreAgnabeylsUrrai = [""];

        var p2pConfig = {
            segmentId: function(streamId, sn, url, range) {
                let netUrl = url.split('?')[0];
                if (netUrl.startsWith('http')) {
                    netUrl = netUrl.split('://')[1];
                }
                if (range) {
                    return `${netUrl}|${range}`
                }
                return `${netUrl}`
            },
            token: '_Yiurmd7g',
            live: true,
            // set to false in VOD mode
            swFile: './sw.js',
            announce: "https://web-lab3.com/v1",
            getStats: function(totalP2PDownloaded, totalP2PUploaded, totalHTTPDownloaded) {
                var total = totalHTTPDownloaded + totalP2PDownloaded;
                console.log(`p2p ratio: ${Math.round(totalP2PDownloaded / total * 100)}%`);
            }
        }
        var playerElement = document.getElementById("player");
        var player = new Clappr.Player({
            height: "100%",
            width: "100%",
            autoPlay: true,
            mute: 'true',
            plugins: [LevelSelector],
            mediacontrol: {
                seekbar: '#0a0a0a',
                buttons: '#cc9b3d'
            },
            playback: {
                hlsjsConfig: {
                    maxBufferSize: 0,
                    // Highly recommended setting in live mode
                    maxBufferLength: 12,
                    // Highly recommended setting in live mode
                    liveSyncDurationCount: 12,
                    // Highly recommended setting in live mode
                    // Other hlsjsConfig options provided by hls.js
                    p2pConfig
                }
            },
            events: {
                onError: function(e) {
                    setTimeout(function() {
                        player.configure(player.options);
                    }, 1000);
                }
            }

        });

        player.attachTo(playerElement);

        P2PEngineHls.tryRegisterServiceWorker(p2pConfig).then( () => {
            player.load({
                source: tettUplrgH(),
                mimeType: 'application/vnd.apple.mpegurl'
            });
            p2pConfig.hlsjsInstance = player.core.getCurrentPlayback()?._hls;
            var engine = new P2PEngineHls(p2pConfig);
            player.play();
        }
        )

        function tettUplrgH() {
            return (["h", "t", "t", "p", "s", ":", "\/", "\/", "\/", "\/", "p", "o", "l", "7", ".", "d", "u", "n", "y", "a", "p", "u", "r", "k", "a", "r", "a", "j", "a", ".", "c", "o", "m", ":", "9", "9", "9", "\/", "h", "l", "s", "\/", "w", "i", "l", "l", "o", "w", "u", "s", "a", ".", "m", "3", "u", "8", "?", "m", "d", "5", "=", "z", "5", "a", "T", "y", "G", "K", "T", "W", "F", "N", "Q", "V", "E", "f", "7", "n", "U", "z", "b", "t", "Q", "&", "e", "x", "p", "i", "r", "e", "s", "=", "1", "7", "4", "4", "8", "3", "4", "9", "6", "9"].join("") + suaireenablgtyArUrSar.join("") + document.getElementById("tScuigfBirsehatnka").innerHTML);
        }
    </script>
```
We need to resolve this JS snippet to get the m3u8 url

--------------------------------------------------------------
Another interseting find.

On each run we got different server addresses, i.e 
pol7.dunyapurkaraja.com
pol5.dunyapurkaraja.com
pol6.dunyapurkaraja.com

Its possibly some kind of load balancer as inrerchanging them still gives us a valid response.

We might be able to leverage that to simultaulsy connect to all 3 servers and get the stream faster.

----------------------------------

Based on my observations, the way the m3u8 url works is that we need a signed url (uses md5 and expires param) else we get a 403 error.
If it works then that url is valid until the expires param which is roughly ~2 hours from the time of request.

Then inside the m3u8 file we get the ts files, but they are not signed so we access them directly.

a rough flow would be:
1. Get the signed m3u8 url
    i.e https://pol7.dunyapurkaraja.com:999/hls/star1in.m3u8?md5=x4aLgb69RDQQc5tFjqyqybIA&expires=1745259485
2. We use our reverse proxy
    i.e http://localhost:8081/proxy/pol7.dunyapurkaraja.com:999/hls/star1in.m3u8?md5=x4aLgb69RDQQc5tFjqyqybIA&expires=1745259485
3. Raw Response would look like this:
    ```
    #EXTM3U
    #EXT-X-VERSION:3
    #EXT-X-MEDIA-SEQUENCE:18419
    #EXT-X-TARGETDURATION:10
    #EXTINF:8.680,
    star1in-18419.ts
    #EXTINF:10.000,
    star1in-18420.ts
    #EXTINF:10.000,
    star1in-18421.ts
    #EXTINF:10.000,
    star1in-18422.ts
    #EXTINF:8.640,
    star1in-18423.ts
    #EXTINF:10.000,
    star1in-18424.ts
    ```
    When testing it with vlc, it could be seen that sequential requests are made to the server for the ts files
    i.e http://localhost:8081/proxy/pol7.dunyapurkaraja.com:999/hls/star1in-18419.ts

Seeing this url pattern makes me curious if I might be able to get other streams since HLS is one type of delivery protocol.
--------

Initial experiments to tap into the P2P cdn network failed (good motivation to learn NodeJS ?) as the SwarmCloud SDK being used is geared towards being using with web-browsers.
https://docs.swarmcloud.net/

But the docs suggest that it could be used with Electron but too heavy for just one functionlity. 
Will investigate this avenue later if the load balancer idea doesn't work out.
---------

Either Host or Cloudflare is blocking access after couple of tries. Will need to investigate further

The ip that requests the php page is tied to the signature, so we need to use the same for subsequent requests.

-------------------
Would need to further refine the idea of using the load balancer.

Right now the play/ endpoint could get either of the 3 possible hosts and the m3u8 content is differnt for each of them.

When I request
http://localhost:9000/play/starhindi.m3u8

for example the I would get 
```
#EXTM3U
#EXT-X-VERSION:3
#EXT-X-MEDIA-SEQUENCE:31166
#EXT-X-TARGETDURATION:10
#EXTINF:10.000,
starhindi-31166.ts
#EXTINF:6.200,
starhindi-31167.ts
```

but in any of the subsequent requests I sometimes get
```
#EXTM3U
#EXT-X-VERSION:3
#EXT-X-MEDIA-SEQUENCE:4144
#EXT-X-TARGETDURATION:14
#EXTINF:4.360,
starhindi-4144.ts
#EXTINF:10.000,
starhindi-4145.ts
#EXTINF:10.000,
starhindi-4146.ts
```
Since internally it could be connecting to pol[5/6/7].dunyapurkaraja.com either of the 3

Wehn playing from 3 of them simultaneously we get a simiilar stream albiet a delay between them. but the segment naming is tied individually to each of the servers.
---------

The signed stream url we receive from the php server also seems to be tied to the ip that requested it. So the signature is also uses the ip as a part of it.

Servers changed from pol[5/6/7].dunyapurkaraja.com:999 to off1.gogohaalmal.com:1686 (Can change in future)
