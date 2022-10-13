let ok = false;
ymaps.ready(init);

function init() {
    let myPlacemark,
        myMap;
    $('#toggle').bind({
        click: function () {
            if (myMap == null) {
                myMap = new ymaps.Map('map', {
                    center: [55.753994, 37.622093], // Новосибирск
                    zoom: 9
                }, {
                    searchControlProvider: 'yandex#search'
                });
                let coords;
                let coord_x_y = document.getElementById('map_coords').value;
                let x, y;
                if (coord_x_y !== null && coord_x_y !== '') {
                    coord_x_y = coord_x_y.split(',')
                    x = coord_x_y[0];
                    y = coord_x_y[1];
                }
                if (!ok) {
                    ok = true;
                    coords = [x, y]
                    myPlacemark = createPlacemark(coords);
                    myMap.geoObjects.add(myPlacemark);
                    // Слушаем событие окончания перетаскивания на метке.
                    myPlacemark.events.add('dragend', function () {
                        getAddress(myPlacemark.geometry.getCoordinates());
                    });
                    getAddress(coords);
                }

                $("#toggle").attr('value', 'Скрыть карту');
                myMap.events.add('click', function (e) {
                    let coords = e.get('coords');
                    // Если метка уже создана – просто передвигаем ее.
                    if (myPlacemark) {
                        myPlacemark.geometry.setCoordinates(coords);
                    }
                    // Если нет – создаем.
                    else {
                        myPlacemark = createPlacemark(coords);
                        myMap.geoObjects.add(myPlacemark);
                        // Слушаем событие окончания перетаскивания на метке.
                        myPlacemark.events.add('dragend', function () {
                            getAddress(myPlacemark.geometry.getCoordinates());
                        });
                    }
                    getAddress(coords);
                    document.getElementById('map_coords').value = coords;

                });
            } else {
                myPlacemark = null;
                ok = false;
                myMap.destroy();// Деструктор карты
                myMap = null;
                $("#toggle").attr('value', 'Показать карту снова');
            }

            // Создание метки.
            function createPlacemark(coords) {
                return new ymaps.Placemark(coords, {
                    iconCaption: 'поиск...'
                }, {
                    preset: 'islands#violetDotIconWithCaption',
                    draggable: true
                });
            }

            // Определяем адрес по координатам (обратное геокодирование).
            function getAddress(coords) {
                myPlacemark.properties.set('iconCaption', 'поиск...');
                ymaps.geocode(coords).then(function (res) {
                    var firstGeoObject = res.geoObjects.get(0);
                    myPlacemark.properties
                        .set({
                            // Формируем строку с данными об объекте.
                            iconCaption: [
                                // Название населенного пункта или вышестоящее административно-территориальное образование.
                                firstGeoObject.getLocalities().length ? firstGeoObject.getLocalities() : firstGeoObject.getAdministrativeAreas(),
                                // Получаем путь до топонима, если метод вернул null, запрашиваем наименование здания.
                                firstGeoObject.getThoroughfare() || firstGeoObject.getPremise()
                            ].filter(Boolean).join(', '),
                            // В качестве контента балуна задаем строку с адресом объекта.
                            balloonContent: firstGeoObject.getAddressLine()
                        });
                    if (firstGeoObject.getLocalities().length === 0) {
                        document.getElementById('filter_coords').value = myPlacemark.properties.getLocalities();
                        console.log(myPlacemark.properties.getLocalities());
                    } else {
                        document.getElementById('filter_coords').value = firstGeoObject.getLocalities()[0];
                        console.log(firstGeoObject.getLocalities()[0]);
                    }
                    console.log(myPlacemark.properties.get('balloonContent'));
                    document.getElementById('map_address').value = myPlacemark.properties.get('balloonContent');
                });
            }
        }
    });
    // Слушаем клик на карте.

}
