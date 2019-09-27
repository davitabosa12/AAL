const fs = require("fs");
const csv = require("csv-parser");
const protobuf = require("protobufjs");
const amqp = require('amqplib/callback_api');
const dgram = require('dgram');
const udpServer = dgram.createSocket('udp4');

const data_recorded = [];
const UDP_PORT = 41214;
const MULTICAST_GROUP = "225.2.2.5";
var Data;
var channel;
var position = 0;
const URL = '192.168.0.123'
const queue = 'location';
var time_t0 = 0;

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
        console.log("Connecting to RabbitMQ");
        
        connectToRabbitMQ(URL, channelMq =>{
            console.log("Binding UDP trigger at " + UDP_PORT);
            
            udpServer.bind(UDP_PORT, () =>{
                udpServer.addMembership(MULTICAST_GROUP);
            });
            channel = channelMq;
            
            
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

function connectToRabbitMQ(url, callback){
    amqp.connect('amqp://user:aalgreat@' + url, (connectError, connection)=>{
        if(connectError){
            throw connectError
        }
        
        connection.createChannel((channelError, channel)=>{
            if(channelError){
                throw channelError
            }
            console.log("Connected.");
            callback(channel);
            
        });
        
    });
}

function sendInfo(){
    //read mock data from internal memory
    var row = data_recorded[position++ % data_recorded.length];
    var time_now = Date.now().valueOf() / 1000;
    const theTime = time_now - time_t0 + "";
    console.log(time_t0);

    var payload = {
        Entity_Id: '123',
        Timestamp: theTime,
        Location: row.LOCATION,
    }
    //create a protocol buffer
    var msg = Data.create(payload); //creating a data obj
    var buffer = Data.encode(msg).finish(); //encoding the data obj to bytes

    //send bytes to RabbitMQ
    console.log(`Sent message to RabbitMQ: ${JSON.stringify(payload)}`);
    channel.sendToQueue(queue, Buffer.from(buffer));
}