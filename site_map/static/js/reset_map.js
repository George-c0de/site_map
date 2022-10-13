async function f() {
    let coords = Number(document.getElementById('delete_map').value);
    console.log(coords)
    if (coords !== 0) {
        $.ajax({
            type: "POST",
            url: "/delete_coords",
            data: {
                coords_id: coords,
            },
            success: function () {
                alert("Точка удалена")
                location.reload();
            }
        })
    }

}