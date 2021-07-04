'use strict';

const overlay = $('#overlay-suggest');

function request(endpoint, obj) {
    return $.ajax({
        type: "POST",
        headers: {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json'
        },
        url: endpoint,
        contentType: 'application/json; charset=UTF-8',
        data: JSON.stringify(obj),
        beforeSend: function () {
            overlay.removeClass('d-none');
        },
        success: function (res) {
            console.info(res);
            overlay.addClass('d-none');
        },
        dataType: "json",
    });
}


$(document).ready(() => {
    const contentBlock = $('#content-block');
    const editBlock = $('#edit-block');
    const headline = $('#headline');
    const sugBlock = $('#sug-block');

    const editMode = $('.edit-mode');
    $('#btn-correct').click(((e) => {
        e.preventDefault();

        editMode.toggle();
        correct();
    }));

    $('#btn-return').click(((e) => {
        editMode.toggle();
    }));

    let meta;
    function correct() {
        const content = contentBlock.val().trim();
        if (!content) return;

        request("/correct", { 'content': content })
            .done((response) => {
                meta = response.meta;
                showEdit(response.edit);
            });
    }

    const rightPtn = /(\{\+(.*?)\/\/(.*?)\+\})/gm;
    const warningPtn = /(\\\*(.*?)\/\/(.*?)\*\\)/gm;
    const wrongPtn = /(\[-(.*?)\/\/(.*?)-\])/gm;

    function showEdit(edit) {
        headline.text('Click the word you want to check.');
        edit = edit
            .replace(rightPtn, "<target class='text-success' data-id='$3'>$2</target>")
            .replace(wrongPtn, "<target class='text-danger' data-id='$3'>$2</target>")
            .replace(warningPtn, "<target class='text-warning' data-id='$3'>$2</target>");
        editBlock.html(edit);
    }

    let prevId = undefined;
    editBlock.click((e) => {
        const id = e.target.dataset.id;
        if (id === undefined) return;
        // else if (prevId === id) return;
        prevId = id;

        const [token, dep] = meta[id].key.split('|');
        headline.text(`${token} - ${meta[id].norm_pattern} (${meta[id].ngram})`);
        request("/suggest", meta[id]).done(showSuggestions);
    });

    function showSuggestions(response) {
        let { suggests } = response;

        if (!suggests) return;

        const suggestsList = suggests.reduce((prev, curr) => {
            const { norm_pattern, percent, ngrams } = curr;
            return prev + `<div>${norm_pattern} (${percent}%)</div>` +
                `<ul>
                    ${ngrams.reduce((pre, ngram) => pre + `<li data-toggle="tooltip" data-placement="left" title="${ngram[0]}">${ngram[1]}</li>`, '')}
                </ul>`;
        }, '');
        sugBlock.html(suggestsList);

        $('[data-toggle="tooltip"]').tooltip();
    }
})