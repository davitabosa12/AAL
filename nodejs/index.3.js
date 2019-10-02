const fs = require("fs");
const csv = require("csv-parser");
const dgram = require('dgram');
const udpServer = dgram.createSocket('udp4');
const net = require('net')
const data_recorded = [];
const UDP_PORT = 41214;
const MULTICAST_GROUP = "225.2.2.5";
var position = 0;
const URL = '192.168.0.123'
const queue = 'location';
var time_t0 = 0;
var gateway_address = null;

if(fs.existsSync("log/log.csv")){
    fs.createReadStream("log/log.csv")
    .pipe(csv({
        separator: ';'
    }))
    .on("data", (row) =>{
        data_recorded.push(row);
    })
    .on("end", () =>{
        console.log("Data read.");
        console.log(data_recorded.length)        
        console.log("Binding UDP trigger at " + UDP_PORT);
        
        udpServer.bind(UDP_PORT, () =>{
            udpServer.addMembership(MULTICAST_GROUP);
        });
    });
}

udpServer.on('listening', () =>{
    console.log(`Waiting for ACTIVATE @ ${MULTICAST_GROUP}:${UDP_PORT}`);
})

udpServer.on('error', error =>{
    console.error(error);

});
udpServer.on('message', (msg, rinfo) =>{
    console.log(msg.toString());
    console.log("Activated. Started sending info every 2 seconds.");
    gateway_address = rinfo.address;
    time_t0 = Date.now().valueOf() / 1000;
    createWindow()
    //setInterval(() => {
    //    sendInfo();    
    //}, 2000);
})
function sendInfo(){
    //read mock data from internal memory
    var client = new net.Socket();
    const PORT = 8077;
    client.connect(PORT, gateway_address, function(){
        var row = data_recorded[position++ % data_recorded.length];
        var time_now = Date.now().valueOf() / 1000;
        const timeDelta = time_now - time_t0 + "";

        var payload = {
            Entity_Id: '123',
            Timestamp: timeDelta,
            Location: row.LOCATION + "_tp",
        }
        const stringified = "JSON\n" + JSON.stringify(payload);
        //send CSV to Gateway
        console.log(`Sent message to ${gateway_address}: ${stringified}`);
        
            client.write(Buffer.from(stringified));
            client.destroy();
    });
}