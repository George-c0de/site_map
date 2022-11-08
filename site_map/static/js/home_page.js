let old_control = null
let object_arr = []
let object_all = []
ymaps.ready(init);
let all_filters = []

function CustomSearchProvider(points) {
    this.points = points;
}

// Провайдер ищет по полю text стандартным методом String.ptototype.indexOf.
CustomSearchProvider.prototype.geocode = function (request, options) {
    let deferred = new ymaps.vow.defer(),
        geoObjects = new ymaps.GeoObjectCollection(),
        // Сколько результатов нужно пропустить.
        offset = options.skip || 0,
        // Количество возвращаемых результатов.
        limit = options.results || 20;
    let points = [];
    // Ищем в свойстве text каждого элемента массива.
    for (let i = 0, l = this.points.length; i < l; i++) {
        let point = this.points[i];
        if (point['properties'].balloonContentHeader.slice(0, -4).toLowerCase().indexOf(request.toLowerCase()) !== -1) {
            points.push(point);
        } else if (point['properties'].balloonContentBody.split('<br/>')[2].slice(12, -1).toLowerCase().indexOf(request.toLowerCase()) !== -1) {
            points.push(point);
        }
    }
    // При формировании ответа можно учитывать offset и limit.
    points = points.splice(offset, limit);
    // Добавляем точки в результирующую коллекцию.
    for (let i = 0, l = points.length; i < l; i++) {
        let point = points[i];
        let coords = point['geometry']['coordinates'];
        let text = point['properties'].balloonContentHeader.slice(0, -4);
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
    for (let i = 0, l = points.length; i < l; i++) {
        let th = document.createElement('tr');
        data_table.insertBefore(th, data_table.firstChild)
        let data_table2 = th;
        let point = points[i];
        let title = document.createElement('th');
        title.scope = "row";
        title.innerHTML = String(points.length - i);
        let fio = document.createElement('td');
        fio.innerHTML = String(point['properties'].balloonContentHeader.slice(0, -4));
        let address = document.createElement('td');
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
    let myMap = new ymaps.Map("map", {
        center: [55.76, 37.64],
        zoom: 10,
        controls: []
    }, {
        searchControlProvider: 'yandex#search'
    })
    let secondButton = new ymaps.control.Button({
        data: {
            // Зададим текст и иконку для кнопки.
            content: "Сбросить",
        },
        options: {
            // Поскольку кнопка будет менять вид в зависимости от размера карты,
            // зададим ей три разных значения maxWidth в массиве.
            maxWidth: [28, 150, 178],
            selectOnClick: false
        }

    });

    function reset_filter(list_filter) {
        for (let i = 0; i < list_filter.length; i += 1) {

            for (let j = 0; j < list_filter[i].getAll().length; j += 1) {
                list_filter[i].getAll()[j].deselect();
            }
        }
    }

    secondButton.events.add('click', function (e) {
        reset_filter(all_filters);
    });
    myMap.controls.add(secondButton);

    let objectManager = new ymaps.ObjectManager({
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

        function set_filter(data, objectManager, myMap, title) {
            let listBoxItems = data
                    .map(function (title) {
                        return new ymaps.control.ListBoxItem({
                            data: {
                                content: title
                            },
                            state: {
                                selected: false
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
                        content: title,
                        title: title
                    },
                    items: listBoxItems,
                    state: {
                        // Признак, развернут ли список.
                        //expanded: true,
                        filters: listBoxItems.reduce(reducer, {})
                    }
                });
            myMap.controls.add(listBoxControl);
            // Добавим отслеживание изменения признака, выбран ли пункт списка.
            listBoxControl.events.add(['select', 'deselect'], function (e) {
                let listBoxItem = e.get('target');
                let filters = ymaps.util.extend({}, listBoxControl.state.get('filters'));
                filters[listBoxItem.data.get('content')] = listBoxItem.isSelected();
                listBoxControl.state.set('filters', filters);
            });
            all_filters.push(listBoxControl);
            return listBoxControl
        }

        function set_monitor(listBoxControl, names) {
            let filterMonitor = new ymaps.Monitor(listBoxControl.state);
            filterMonitor.add('filters', function (filters) {
                if (filters['Москва'] !== "undefined") {
                    object_arr = [];
                }
                object_all = objectManager.objects.getAll()
                myMap.controls.remove(old_control)
                // Применим фильтр.
                let filters_all = []
                for (let i = 0; i < all_filters.length; i += 1) {
                    filters_all.push(ymaps.util.extend({}, all_filters[i].state.get('filters')))
                }
                let new_filters = {};
                for (let i = 0; i < filters_all.length; i += 1) {
                    let er = false;
                    for (let j = 0; j < Object.keys(filters_all[i]).length; j += 1) {
                        if (filters_all[i][Object.keys(filters_all[i])[j]]) {
                            er = true;
                        }
                    }
                    if (er) {
                        new_filters[i] = filters_all[i];
                    }
                }
                objectManager.setFilter(getFilterFunction(new_filters, names))
                //objectManager.setFilter(getFilterFunction(filters, name));

                for (let el in object_all) {
                    if (objectManager.getObjectState(el)['isFilteredOut'] === false) {
                        object_arr.push(objectManager.objects.getAll()[el])
                    }
                }
                if (object_arr.length === 0) {
                    object_arr = objectManager.objects.getAll();
                    objectManager.setFilter(function (object) {
                        return true;
                    })
                }
                let data_table = document.getElementById('data_table')
                while (data_table.firstChild) {
                    data_table.removeChild(data_table.firstChild);
                }
                for (let i = 0, l = object_arr.length; i < l; i++) {
                    let th = document.createElement('tr');
                    data_table.insertBefore(th, data_table.firstChild)
                    let data_table2 = th;
                    let point = object_arr[i];
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
                let mySearchControl = new ymaps.control.SearchControl({
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
        }

        let listBoxControl = set_filter(data['city'], objectManager, myMap, 'Город');
        let listBoxControl2 = set_filter(data['position'], objectManager, myMap, 'Должность');
        let listBoxControl3 = set_filter(data['standard_soft'], objectManager, myMap, 'Cтандартные мягкие контактные линзы');
        let listBoxControl4 = set_filter(data['standard_soft_for_myopia'], objectManager, myMap, 'Специальные мягкие контактные линзы для контроля миопии');

        let listBoxControl5 = set_filter(data['customized_soft_contact_lenses'], objectManager, myMap, 'Индивидуальные мягкие контактные линзы');
        let listBoxControl6 = set_filter(data['soft_contact_lenses_for_keratoconus'], objectManager, myMap, 'Мягкие контактные линзы для кератоконуса');
        let listBoxControl7 = set_filter(data['corneal_rigid'], objectManager, myMap, 'Роговичные жесткие газопроницаемые контактные линзы');
        let listBoxControl8 = set_filter(data['scleral_lenses'], objectManager, myMap, 'Склеральные линзы');
        let listBoxControl9 = set_filter(data['orthokeratological_lenses'], objectManager, myMap, 'Ортокератологические линзы c фиксированным дизайном');
        let listBoxControl10 = set_filter(data['customized_orthokeratological_lenses'], objectManager, myMap, 'Кастомизированные ортокератологические линзы');


        let names = ['city', 'position', 'standard_soft', 'standard_soft_for_myopia', 'customized_soft_contact_lenses', 'soft_contact_lenses_for_keratoconus',
            'corneal_rigid', 'scleral_lenses', 'orthokeratological_lenses', 'customized_orthokeratological_lenses']
        set_monitor(listBoxControl, names)
        set_monitor(listBoxControl2, names)
        set_monitor(listBoxControl3, names)
        set_monitor(listBoxControl4, names)
        set_monitor(listBoxControl5, names)
        set_monitor(listBoxControl6, names)
        set_monitor(listBoxControl7, names)
        set_monitor(listBoxControl8, names)
        set_monitor(listBoxControl9, names)
        set_monitor(listBoxControl10, names)

    });

    function getFilterFunction(categories, name) {
        return function (obj) {
            let res = []
            for (let i = 0; i < Object.keys(categories).length; i += 1) {
                let content = obj.properties.balloonContent[name[Object.keys(categories)[i]]];
                let yes_or_no = false
                if (typeof content == 'object') {
                    for (let j = 0; j < content.length; j += 1) {
                        if (categories[Object.keys(categories)[i]][content[j]] === true) {
                            yes_or_no = true
                        }
                    }
                    res.push(yes_or_no)
                } else {
                    res.push(categories[Object.keys(categories)[i]][content])
                }
            }
            let yes_or_no = true
            for (let i = 0; i < res.length; i += 1) {
                if (res[i] === false) {
                    yes_or_no = false;
                    break;
                }
            }
            return yes_or_no
        }
    }


    $.ajax({
        url: "/get_coords_and_profile"
    }).done(function (data) {
        objectManager.add(data);
        let mySearchControl = new ymaps.control.SearchControl({
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
