// Modify values in [brackets]
// [envoy-ip]: the IP address of your Enphase Envoy modem (web-interface)


// ==UserScript==
// @name         Power Consumption Query
// @namespace    http://[envoy-ip]/home
// @version      0.1
// @description  Plays alarm if power usage high.
// @author       BungyStudios
// @match        http://[envoy-ip]/home
// @grant        none
// ==/UserScript==

var value = document.getElementsByClassName("list-group-item");
var alarm = new Audio("https://www.bungystudios.com/wp-content/uploads/2021/09/loud_alarm.mp3"); // Alarm sound file location

function query() {
    if (value.item(2).getElementsByClassName("units").item(0).innerText == "kW") {
        var consumption = value.item(2).getElementsByClassName("value").item(0).innerText;
        consumption = parseFloat(consumption);
        if (consumption >= 2) { // [threshold]: a float value in kW to trigger alarm
            alarm.play();
        } else {
            // alert("Not exceed");
            alarm.pause();
        }
    }
}

function reload() {
    location.reload(true);
}

setTimeout(query, 10000); // Time in ms after page refresh to query data
setTimeout(reload, 30000); // Time in ms to refresh page for new data
