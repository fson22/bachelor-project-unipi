setInterval(() => {
    fetch('/all_temperatures_heating_mode')
      .then(response => response.json())
      .then(data => {
        // console.log(data);
        Object.keys(data).forEach(roomId => {
          let roomElement = document.getElementById(`temp-${roomId}`);
          let roomContainer = document.getElementById(`${roomId}`)

        //   Zobrazeni teploty
          if (roomElement) {
            roomElement.textContent = `${data[roomId].current_temp}°C`;
          }

          // Monitoring True?
          if(data[roomId].monitoring){
          // Dynamicke pridavani trid pro topeni (ON/OFF)
          roomContainer.classList.remove('monitoringOff');
          roomContainer.classList.add('monitoringOon');
            if (data[roomId].heating_on) {
              roomContainer.classList.remove('off');
              roomContainer.classList.add('on');
            } else {
              roomContainer.classList.remove('on');
              roomContainer.classList.add('off');
            }
  
          //   Dynamicke pridavani trid pro rezimy
            if (data[roomId].mode == 'dayMode'){
              roomContainer.classList.remove('nightMode');
              roomContainer.classList.add('dayMode');
            } else {
              roomContainer.classList.remove('dayMode');
              roomContainer.classList.add('nightMode');
            }
          } else {
            roomContainer.classList.remove('monitoringOn');
            roomContainer.classList.add('monitoringOff');
            roomContainer.classList.add('off');
            roomContainer.classList.remove('dayMode');
            roomContainer.classList.remove('nightMode');
          }
        });
      });

  }, 6000);


window.addEventListener("pageshow", () => {
  document.querySelectorAll(".room").forEach(room => {
    let roomId = room.id;
    fetch(`/monitoring/${roomId}`)
    .then(response => response.json())
    .then(data => {
      if(data.monitoring) {
        // console.log(`Místnost ${room.id} je monitorována`);
        room.classList.remove("monitoringOff");
        room.classList.add("monitoringOn");
      } else {
        // console.log(`Místnost ${room.id} NE monitorována`);
        room.classList.remove("monitoringOn");
        room.classList.add("monitoringOff");
        room.classList.add('off');
        room.classList.remove('on');
        room.classList.remove('dayMode');
        room.classList.remove('nightMode');
      }
    })
    .catch(error => console.error(`Chyba pro nacitani monitoringu pro ${room.id}`));
    
  })

})