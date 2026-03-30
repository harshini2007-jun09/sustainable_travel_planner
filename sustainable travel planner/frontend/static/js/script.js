
async function plan() {
    const res = await fetch('/plan', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({})
    });

    const data = await res.json();
    document.getElementById('results').innerHTML =
        JSON.stringify(data, null, 2);
}
