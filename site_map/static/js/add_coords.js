async function add_coords() {
    let coords_x = document.getElementById('map_coords').value.split(',')[0];
    let coords_y = document.getElementById('map_coords').value.split(',')[1];
    let address = document.getElementById('map_address').value;
    let filter_coords = document.getElementById('filter_coords').value;
    $.ajax({
        type: "POST",
        url: "/add_coord",
        data: {
            coords_x: coords_x,
            coords_y: coords_y,
            address: address,
            filter_coords: filter_coords,
        },
        success: function () {
            alert("Адрес добавлен");
            location.reload();
        }
    })
}