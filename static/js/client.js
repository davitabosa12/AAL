window.onload = function(){
    var socket = io();
    
    var img = document.getElementById("casa");
    var log = document.getElementById("log")

    socket.on('new_position', (position)=>{
        if(position.Location === "kitchen"){
            img.src = "static/images/009.png"
        } else if(position.Location === "dinner"){
            img.src = "static/images/010.png"
        }else if(position.Location === "room"){
            img.src = "static/images/008.png"
        }
        let temp = log.innerHTML;
        log.innerHTML = `\n${position.Timestamp} -> ${position.Location}` + temp
    })

    socket.on('disconnect', ()=>{
        alert("Disconnected");
        img.src = "static/images/001.png";
    })
    
}