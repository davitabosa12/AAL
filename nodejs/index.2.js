const fs = require("fs");
const csv = require("csv-parser");
const protobuf = require("protobufjs");
const amqp = require('amqplib/callback_api');
const dgram = require('dgram');
const udpServer = dgram.createSocket('udp4');
const ArgumentParser = require('argparse').ArgumentParser;
const net = require('net')

const data_recorded = [];
const UDP_PORT = 41214;
const MULTICAST_GROUP = "225.2.2.5";
var Data;
var gateway_address = "";
var position = 0;
var time_t0 = 0;

var parser = new ArgumentParser({
    version: '0.0.1',
    addHelp:true,
});

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
        loadProtobuf();
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
    console.log(rinfo);
    gateway_address = rinfo.address;
    console.log(msg.toString());
    console.log("Activated. Started sending info every 2 seconds.");
    time_t0 = Date.now().valueOf() / 1000;
    setInterval(() => {
        sendInfo();    
    }, 2000);
})


function loadProtobuf(){
    console.log("Loading protocol buffer...")
    protobuf.load("data.proto", (err, root) =>{
        
        Data = root.lookupType("Data");
        console.log("protobuf loaded.")
    });
}

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
            Location: row.LOCATION,
        }
        //create a protocol buffer
        var msg = Data.create(payload); //creating a data obj
        var buffer = Data.encode(msg).finish(); //encoding the data obj to bytes

        //send bytes to Gateway
        console.log(`Sent message to ${gateway_address}: ${JSON.stringify(payload)}`);
        
            client.write(Buffer.from(buffer));
            client.destroy();
    });
}