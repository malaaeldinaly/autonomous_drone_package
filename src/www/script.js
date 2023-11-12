document.addEventListener("DOMContentLoaded", function() {
    const takeoffButton = document.getElementById("takeoffButton");
    const landButton = document.getElementById("landButton");
    const armButton = document.getElementById("armButton");
    const disarmButton = document.getElementById("disarmButton");

    const mavlinkServerUrl = "http://localhost:5760"; // Default PX4 SITL MAVLink URL

    takeoffButton.addEventListener("click", () => {
        console.log("Takeoff button clicked");
        sendCommand("cmd_long_takeoff");
    });

    landButton.addEventListener("click", () => {
        console.log("Land button clicked");
        sendCommand("cmd_long_land");
    });

    armButton.addEventListener("click", () => {
        console.log("Arm button clicked");
        /*sendCommand("cmd_long_arm");*/
    });

    disarmButton.addEventListener("click", () => {
        console.log("Disarm button clicked");
        /*sendCommand("cmd_long_disarm");*/
    });

    function sendCommand(command) {
        const xhr = new XMLHttpRequest();
        xhr.open("GET", `${mavlinkServerUrl}/mavlink/${command}`);
        xhr.send();
    }
});