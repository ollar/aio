var textarea = document.getElementById('content');

function beatify(e) {
    var el = e.target;
    var val = el.value;
    try {
        val = JSON.parse(val);
        el.value = JSON.stringify(val, null, 2);
    } catch (e) {
        console.log('json parse error')
    }
}

textarea.addEventListener('blur', beatify);
