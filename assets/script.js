function scroll() {
    if (window.innerWidth <= 600) {
        var element = document.getElementById("body");
        element.scrollIntoView({behavior: "smooth"});
    }
}

var checkExist = setInterval(function() {
    try {
        document.getElementById("show-chs-cases").addEventListener("click", scroll);
        document.getElementById("show-chs-deaths").addEventListener("click", scroll);
        document.getElementById("show-sc-cases").addEventListener("click", scroll);
        document.getElementById("show-sc-deaths").addEventListener("click", scroll);
        clearInterval(checkExist);
    } catch (err) {}
}, 100);
