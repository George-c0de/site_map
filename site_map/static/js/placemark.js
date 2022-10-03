let response = [];

async function load_data() {
    let res = await fetch('/get_coords_and_profile')
    let data = await res.json();
    response = data;
    ymaps.ready(init);
}

load_data();

function CustomSearchProvider(points) {
    this.points = points;
}

// Провайдер ищет по полю text стандартным методом String.ptototype.indexOf.
CustomSearchProvider.prototype.geocode = function (request, options) {
    var deferred = new ymaps.vow.defer(),
        geoObjects = new ymaps.GeoObjectCollection(),
        // Сколько результатов нужно пропустить.
        offset = options.skip || 0,
        // Количество возвращаемых результатов.
        limit = options.results || 20;

    var points = [];
    // Ищем в свойстве text каждого элемента массива.
    for (var i = 0, l = this.points.length; i < l; i++) {
        var point = this.points[i];
        if (point.text.toLowerCase().indexOf(request.toLowerCase()) !== -1) {
            points.push(point);
        }
    }
    // При формировании ответа можно учитывать offset и limit.
    points = points.splice(offset, limit);
    // Добавляем точки в результирующую коллекцию.
    for (var i = 0, l = points.length; i < l; i++) {
        var point = points[i],
            coords = point.coords,
            text = point.text;

        geoObjects.add(new ymaps.Placemark(coords, {
            name: text + ' name',
            description: text + ' description',
            balloonContentBody: '<p>' + text + '</p>',
            boundedBy: [coords, coords]
        }));
    }

    deferred.resolve({
        // Геообъекты поисковой выдачи.
        geoObjects: geoObjects,
        // Метаинформация ответа.
        metaData: {
            geocoder: {
                // Строка обработанного запроса.
                request: request,
                // Количество найденных результатов.
                found: geoObjects.getLength(),
                // Количество возвращенных результатов.
                results: limit,
                // Количество пропущенных результатов.
                skip: offset
            }
        }
    });

    // Возвращаем объект-обещание.
    return deferred.promise();
};

function init() {
    let myCollection = new ymaps.GeoObjectCollection();
    let x = response.x;
    let y = response.y;
    let first_name = response.first_name;
    let email = response.email;
    let last_name = response.last_name;
    let patronymic = response.patronymic;
    let image = response.image;
    let address = response.address;
    x = x.split(',');
    y = y.split(',');
    var myMap = new ymaps.Map("map", {
            center: [55.76, 37.64],
            zoom: 10,
            controls: []
        }, {
            searchControlProvider: 'yandex#search'
        });

    $.ajax({
        url: "/get_coords_and_profile"
    }).done(function (data) {
        objectManager.add(data);
    });
    let myPoints = []
    for (let i = 0; i < x.length; i += 1) {
        let new_point = new ymaps.Placemark([x[i], y[i]], {
            balloonContentHeader: address[i] + '<br>',
            // Зададим содержимое основной части балуна.
            balloonContentBody: '<img alt="картинка" src="' + image[i] + '" height="150" width="200" class="scale"> <br/> ' +
                '<b>Email:</b><br/><p>' + email[i] +
                '<br/><b>ФИО</b><br/> Имя: ' + first_name[i] + '<br>Фамилия:' + last_name[i] + '<br>Отчество: ' + patronymic[i] + '<br>Адрес: ' + address[i] + '</p>',
            // Зададим содержимое нижней части балуна.
            balloonContentFooter: 'Информация предоставлена:<br/>OOO "Рога и копыта"',
            // Зададим содержимое всплывающей подсказки.
            hintContent: '<img alt="картинка" src="' + image + '" height="100" width="100" >',
            balloonContent: 'Школа',
            clusterCaption: 'Школа',
        })

        function checkState() {
            var shownObjects,
                byColor = new ymaps.GeoQueryResult(),
                byShape = new ymaps.GeoQueryResult();

            // Отберем объекты по цвету.
            if ($('#red').prop('checked')) {
                // Будем искать по двум параметрам:
                // - для точечных объектов по полю preset;
                // - для контурных объектов по цвету заливки.
                byColor = myObjects.search('options.fillColor = "#ff1000"')
                    .add(myObjects.search('options.preset = "islands#redIcon"'));
            }
            if ($('#green').prop('checked')) {
                byColor = myObjects.search('options.fillColor = "#00ff00"')
                    .add(myObjects.search('options.preset = "islands#greenIcon"'))
                    // После того, как мы нашли все зеленые объекты, добавим к ним
                    // объекты, найденные на предыдущей итерации.
                    .add(byColor);
            }
            if ($('#yellow').prop('checked')) {
                byColor = myObjects.search('options.fillColor = "#ffcc00"')
                    .add(myObjects.search('options.preset = "islands#yellowIcon"'))
                    .add(byColor);
            }
            // Отберем объекты по форме.
            if ($('#point').prop('checked')) {
                byShape = myObjects.search('geometry.type = "Point"');
            }
            if ($('#polygon').prop('checked')) {
                byShape = myObjects.search('geometry.type = "Polygon"').add(byShape);
            }
            if ($('#circle').prop('checked')) {
                byShape = myObjects.search('geometry.type = "Circle"').add(byShape);
            }

            // Мы отобрали объекты по цвету и по форме. Покажем на карте объекты,
            // которые совмещают нужные признаки.
            shownObjects = byColor.intersect(byShape).addToMap(myMap);
            // Объекты, которые не попали в выборку, нужно убрать с карты.
            myObjects.remove(shownObjects).removeFromMap(myMap);
        }

        myCollection.add(new_point);
        let temp_text = address[i] + email[i];
        if (first_name[i] !== 'Не указано') {
            temp_text = temp_text + first_name[i]
        }
        if (last_name[i] !== 'Не указано') {
            temp_text = temp_text + last_name[i]
        }
        if (patronymic[i] !== 'Не указано') {
            temp_text = temp_text + patronymic[i]
        }
        var point = {
            coords: [x[i], y[i]],
            text: temp_text,
        };
        myPoints.push(point);

    }
    myMap.geoObjects.add(myCollection);
    var mySearchControl = new ymaps.control.SearchControl({
        options: {
            // Заменяем стандартный провайдер данных (геокодер) нашим собственным.
            provider: new CustomSearchProvider(myPoints),
            // Не будем показывать еще одну метку при выборе результата поиска,
            // т.к. метки коллекции myCollection уже добавлены на карту.
            noPlacemark: true,
            resultsPerPage: 5
        }
    });

    // Добавляем контрол в верхний правый угол,
    myMap.controls
        .add(mySearchControl, {float: 'right'});
}
