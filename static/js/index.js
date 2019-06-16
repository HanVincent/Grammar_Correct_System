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
        beforeSend: function() {
            overlay.removeClass('d-none'); 
        },
        success: function(res) {
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
    const sugTable = $('#sug-table');

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
        else if (prevId === id) return;
        else prevId = id;

        headline.text(meta[id].lemma + ' (' + meta[id].bef + ')');
        request("/suggest", meta[id])
            .done(showSuggestions);
    });

    function showSuggestions(response) {
        let { info } = response;

        if (!info) return;

        const sugList = info.reduce((prev, curr) => {
            const { ptn, percent, ngrams } = curr;
            return prev + `<tr>
            <th scope="row" rowspan=${ngrams.length}>${ptn} (${percent}%)</th><td>${ngrams[0]}</td>
            </tr>` + ngrams.slice(1).reduce((pre, ngram) => {
                    return pre + `<tr><td>${ngram}</td></tr>`
                }, '');

        }, '')
        sugTable.html(sugList);
    }
})