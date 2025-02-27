// Toggle switch
const checkbox = document.getElementById("roomModeSwitch");
checkbox.addEventListener('change', () => {
  fetch(`/room/${room_id}/update_monitoring`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      monitoring: checkbox.checked
    })
  })
  .then(response => response.json())
  .catch(error => {
    console.error('Error: ', error);
  })
})


// Nastavovani teploty rucne
const setterTemp = document.getElementById('myRange');
const setterTempDisplay = document.getElementById('sliderValue');

// Zmena teploty dle posuvniku
setterTemp.addEventListener('input', () => {
  targetTemp = setterTemp.value
  setterTempDisplay.textContent = targetTemp;
});

document.getElementById("setTargetTemperature").addEventListener("click", () => {
  fetch(`/room/${room_id}/set_target_temperature`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      targetTemp: targetTemp
    })
  })
  .then(response => response.json())
  // .then(data => {
  //   // alert(data.status); 
  // })
  .catch(error => {
    console.error('Error: ', error)
  })

  // Ziskani aktualni cilove teploty
  fetch(`/room/${room_id}/get_target_temperature`)
    .then(response => response.json())
    .then(data => {
      setterTemp.value = data.targetTemp || 'N/A';
    });
})

// Periodicke aktualizace teploty
setInterval(() => {
  fetch(`/room/${room_id}/temperature`)
  .then(response => response.json())
  .then(data => {
    document.getElementById('currentTemp').querySelector('h4').textContent = data.temperature || 'Error';
  });
}, 6000);





// ////////////////////
// // REZIMY

// DENNI REZIM
// Denní teplota
const dayTempTarget = document.getElementById('dayTemp');
const dayTempDisplay = document.getElementById('dayTempValue');

// Změna denní teploty
dayTempTarget.addEventListener('input', () => {
  dayTempDisplay.textContent = dayTempTarget.value;
});

// Odeslani pozadavku na server
document.getElementById('saveDaySettings').addEventListener('click', () =>{
  const dayModeTimeStart = document.getElementById('dayStart').value; 
  const dayModeTimeEnd = document.getElementById("dayEnd").value;
  fetch(`/room/${room_id}//set_day_mode`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      dayTempTarget: dayTempTarget.value,
      dayModeTimeStart: dayModeTimeStart,
      dayModeTimeEnd: dayModeTimeEnd
    })
  })
  .then(response => response.json())
  .then(data => {
    // alert(data.status)
  })
  .catch(error => {
    console.error('Error: ', error)
  })
});


// NOCNI REZIM
// Noční teplota
const nightTempTarget = document.getElementById('nightTemp');
const nightTempDisplay = document.getElementById('nightTempValue');

// Změna noční teploty
nightTempTarget.addEventListener('input', () => {
  nightTempDisplay.textContent = nightTempTarget.value;
});

// Odeslani pozadavku na server
document.getElementById('saveNightSettings').addEventListener('click', () => {
  // const nightModeTimeStart = document.getElementById('nightStart').value;
  // const nightModeTimeEnd = document.getElementById('nightEnd').value
  fetch(`/room/${room_id}/set_night_mode`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      nightTempTarget: nightTempTarget.value,
      // nightModeTimeStart: nightModeTimeStart,
      // nightModeTimeEnd: nightModeTimeEnd
    })
  })
  .then(response => response.json())
  .then(data => {
    // alert(data.status)
  })
  .catch(error => {
    console.error('Error: ', error)
  })
})