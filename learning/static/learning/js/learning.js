$(function () {
    $('[data-toggle="tooltip"]').tooltip()
});

$("#id_username").keypress(function () {
    let username = $(this).val();
    $.ajax({
        url: '/accounts/ajax/search/',
        data: {
            'user': username
        },
        dataType: 'json',
        success: function (data) {
            let user_list = $("#user_list");
            user_list.empty();
            for (let i = 0; i < data.length; i++) {
                // noinspection JSUnresolvedVariable
                user_list.append("<option value='" + data[i].username + "' label='" + data[i].first_name + ' ' + data[i].last_name + "'></option>");
            }
        }
    });
});
