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

Another interseting find.

On each run we got different server addresses, i.e 
pol7.dunyapurkaraja.com
pol5.dunyapurkaraja.com
pol6.dunyapurkaraja.com

Its possibly some kind of load balancer as inrerchanging them still gives us a valid response.

We might be able to leverage that to simultaulsy connect to all 3 servers and get the stream faster.