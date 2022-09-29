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
        if (point.text.toLowerCase().indexOf(request.toLowerCase()) != -1) {
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
        }),
        objectManager = new ymaps.ObjectManager({
            // Чтобы метки начали кластеризоваться, выставляем опцию.
            clusterize: true,
            // ObjectManager принимает те же опции, что и кластеризатор.
            gridSize: 64,
            // Макет метки кластера pieChart.
            clusterIconLayout: "default#pieChart"
        });
    myMap.geoObjects.add(objectManager);
    var listBoxItems = ['Школа', 'Аптека', 'Магазин', 'Больница', 'Бар']
            .map(function (title) {
                return new ymaps.control.ListBoxItem({
                    data: {
                        content: title
                    },
                    state: {
                        selected: true
                    }
                })
            }),
        reducer = function (filters, filter) {
            filters[filter.data.get('content')] = filter.isSelected();
            return filters;
        },
        // Теперь создадим список, содержащий 5 пунктов.
        listBoxControl = new ymaps.control.ListBox({
            data: {
                content: 'Фильтр',
                title: 'Фильтр'
            },
            items: listBoxItems,
            state: {
                // Признак, развернут ли список.
                expanded: true,
                filters: listBoxItems.reduce(reducer, {})
            }
        });
    myMap.controls.add(listBoxControl);
    listBoxControl.events.add(['select', 'deselect'], function (e) {
        var listBoxItem = e.get('target');
        var filters = ymaps.util.extend({}, listBoxControl.state.get('filters'));
        filters[listBoxItem.data.get('content')] = listBoxItem.isSelected();
        listBoxControl.state.set('filters', filters);
    });

    var filterMonitor = new ymaps.Monitor(listBoxControl.state);
    filterMonitor.add('filters', function (filters) {
        // Применим фильтр.
        objectManager.setFilter(getFilterFunction(filters));
    });

    function getFilterFunction(categories) {
        return function (obj) {
            var content = obj.properties.balloonContent;
            return categories[content]
        }
    }

    let myPoints = []
    for (let i = 0; i < x.length; i += 1) {
        let new_point = new ymaps.Placemark([x[i], y[i]], {
            balloonContentHeader: address[i] + '<br>',
            // Зададим содержимое основной части балуна.
            balloonContentBody: '<img src="' + image[i] + '" height="150" width="200" class="scale"> <br/> ' +
                '<b>Email:</b><br/><p>' + email[i] +
                '<br/><b>ФИО</b><br/> Имя: ' + first_name[i] + '<br>Фамилия:' + last_name[i] + '<br>Отчество: ' + patronymic[i] + '<br>Адрес: ' + address[i] + '</p>',
            // Зададим содержимое нижней части балуна.
            balloonContentFooter: 'Информация предоставлена:<br/>OOO "Рога и копыта"',
            // Зададим содержимое всплывающей подсказки.
            hintContent: '<img src="' + image + '" height="100" width="100" >',
            balloonContent: 'Школа',
            clusterCaption: 'Школа',

        })
        myCollection.add(new_point);
        objectManager.add(new_point);
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
