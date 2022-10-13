var old_control = null
ymaps.ready(init);

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
        if (point['properties'].balloonContentHeader.slice(0, -4).toLowerCase().indexOf(request.toLowerCase()) !== -1) {
            points.push(point);
        } else if (point['properties'].balloonContentBody.split('<br/>')[2].slice(12, -1).toLowerCase().indexOf(request.toLowerCase()) !== -1) {
            points.push(point);
        }
    }
    // При формировании ответа можно учитывать offset и limit.
    points = points.splice(offset, limit);
    // Добавляем точки в результирующую коллекцию.
    for (var i = 0, l = points.length; i < l; i++) {
        var point = points[i];
        var coords = point['geometry']['coordinates'];
        var text = point['properties'].balloonContentHeader.slice(0, -4);
        geoObjects.add(new ymaps.Placemark(coords, {
            name: point['properties'].balloonContentHeader.slice(0, -4),
            description: point['properties'].balloonContentHeader.slice(0, -4),
            balloonContentBody: '<p>' + text + '</p>',
            boundedBy: [coords, coords]
        }));
    }
    let data_table = document.getElementById('data_table')
    while (data_table.firstChild) {
        data_table.removeChild(data_table.firstChild);
    }
    for (var i = 0, l = points.length; i < l; i++) {
        let th = document.createElement('tr');
        data_table.insertBefore(th, data_table.firstChild)
        let data_table2 = th;
        var point = points[i];
        var title = document.createElement('th');
        title.scope = "row";
        title.innerHTML = String(points.length - i);
        var fio = document.createElement('td');
        fio.innerHTML = String(point['properties'].balloonContentHeader.slice(0, -4));
        var address = document.createElement('td');
        address.innerHTML = String(point['properties'].balloonContentBody.split('<b>')[2].slice(4, -1));
        data_table2.insertBefore(fio, data_table2.firstChild);
        data_table2.insertBefore(address, data_table2.firstChild);
        data_table2.insertBefore(title, data_table2.firstChild);
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
    // Создадим 5 пунктов выпадающего списка.
    $.ajax({
        url: "/get_filter"
    }).done(function (data) {
            var listBoxItems = data
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
            // Добавим отслеживание изменения признака, выбран ли пункт списка.
            listBoxControl.events.add(['select', 'deselect'], function (e) {
                var listBoxItem = e.get('target');
                var filters = ymaps.util.extend({}, listBoxControl.state.get('filters'));
                filters[listBoxItem.data.get('content')] = listBoxItem.isSelected();
                listBoxControl.state.set('filters', filters);
            });

            var filterMonitor = new ymaps.Monitor(listBoxControl.state);

            filterMonitor.add('filters', function (filters) {
                myMap.controls.remove(old_control)
                // Применим фильтр.
                objectManager.setFilter(getFilterFunction(filters));
                let object_arr = []
                for (let el in objectManager.objects.getAll()) {
                    if (objectManager.getObjectState(el)['isFilteredOut'] === false) {
                        object_arr.push(objectManager.objects.getAll()[el])
                    }
                }
                let data_table = document.getElementById('data_table')
                while (data_table.firstChild) {
                    data_table.removeChild(data_table.firstChild);
                }
                for (var i = 0, l = object_arr.length; i < l; i++) {
                    let th = document.createElement('tr');
                    data_table.insertBefore(th, data_table.firstChild)
                    let data_table2 = th;
                    var point = object_arr[i];
                    var title = document.createElement('th');
                    title.scope = "row";
                    title.innerHTML = String(object_arr.length - i);
                    var fio = document.createElement('td');
                    fio.innerHTML = String(point['properties'].balloonContentHeader.slice(0, -4));
                    var address = document.createElement('td');
                    address.innerHTML = String(point['properties'].balloonContentBody.split('<b>')[2].slice(4, -1));
                    data_table2.insertBefore(fio, data_table2.firstChild);
                    data_table2.insertBefore(address, data_table2.firstChild);
                    data_table2.insertBefore(title, data_table2.firstChild);
                }
                var mySearchControl = new ymaps.control.SearchControl({
                    options: {
                        // Заменяем стандартный провайдер данных (геокодер) нашим собственным.
                        provider: new CustomSearchProvider(object_arr),
                        // Не будем показывать еще одну метку при выборе результата поиска,
                        // т.к. метки коллекции myCollection уже добавлены на карту.
                        noPlacemark: true,
                        resultsPerPage: 5
                    }
                })
                old_control = mySearchControl
                myMap.controls
                    .add(mySearchControl, {float: 'right'});
            });

            function getFilterFunction(categories) {
                return function (obj) {
                    var content = obj.properties.balloonContent;
                    return categories[content]
                }
            }
        }
    );
    $.ajax({
        url: "/get_coords_and_profile"
    }).done(function (data) {
        objectManager.add(data);
        var mySearchControl = new ymaps.control.SearchControl({
            options: {
                // Заменяем стандартный провайдер данных (геокодер) нашим собственным.
                provider: new CustomSearchProvider(objectManager.objects.getAll()),
                // Не будем показывать еще одну метку при выборе результата поиска,
                // т.к. метки коллекции myCollection уже добавлены на карту.
                noPlacemark: true,
                resultsPerPage: 5
            }
        });
        // Добавляем контрол в верхний правый угол,
        myMap.controls
            .add(mySearchControl, {float: 'right'});
        old_control = mySearchControl
    });


}
