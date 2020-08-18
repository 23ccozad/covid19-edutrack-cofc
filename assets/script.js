/* On larger screens (tablets and computers), the dashboard is shown with the graph on the left and the stats/buttons
on the right. On smaller screens, the graph and stats/buttons are all in one column. This function scrolls the page up
to the graph when he/she taps on any "Show Graph" buttons. Without this, the user would have to scroll up on their own,
which is not intutive. */

// Scrolls the page up if the window is less than 600px wide
function scroll() {
    if (window.innerWidth <= 600) {
        var element = document.getElementById("body");
        element.scrollIntoView({behavior: "smooth"});
    }
}

// Adds a listener for button clicks every 0.1 seconds.
/* Note: I have not found a good way to add the event listeners once the page loads, so the alternative I've developed
is to add the event listeners every 0.1 seconds instead. Not a great solution, but it works. */
var checkExist = setInterval(function() {
    try {
        document.getElementById("show-downtown-cases").addEventListener("click", scroll);
        document.getElementById("show-chs-cases").addEventListener("click", scroll);
        document.getElementById("show-chs-deaths").addEventListener("click", scroll);
        document.getElementById("show-sc-cases").addEventListener("click", scroll);
        document.getElementById("show-sc-deaths").addEventListener("click", scroll);
        clearInterval(checkExist);
    } catch (err) {}
}, 100);