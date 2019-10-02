window.onload = function(){
    var socket = io();
    
    var img = document.getElementById("casa");
    var log = document.getElementById("log")

    socket.on('new_position', (position)=>{
        /*if(position.Location === "kitchen_tp"){
            img.src = "static/images/009.png"
        } else if(position.Location === "dinner_tp"){
            img.src = "static/images/010.png"
        } else if(position.Location === "room_tp"){
            img.src = "static/images/008.png"
        } else if(position.Location === "entrance"){

        }*/

        switch(position.Location){
            case "kitchen_tp":
                img.src = "static/images/009.png"
                break;
            case "dinner_tp":
                img.src = "static/images/010.png"
                break;
            case "room_tp":
                img.src = "static/images/008.png"
                break;
            case "entrance":
                img.src = "static/images/002.png"
                break;
            case "room1":
                img.src = "static/images/003.png"
                break;
            case "room2":
                img.src = "static/images/006.png"
                break;
            case "kitchen":
                img.src = "static/images/004.png"    
                break;
            case "bathroom":
                img.src = "static/images/005.png"
                break;
            case "bedroom":
                img.src = "static/images/007.png"
                break;
        }
        let temp = log.innerHTML;
        log.innerHTML = `\n${position.Timestamp} -> ${position.Location}` + temp
    })

    socket.on('disconnect', ()=>{
        alert("Disconnected");
        img.src = "static/images/001.png";
    })
    
}