'use strict';

$(document).ready(() => {
    const contentBlock = $('#content-block');
    const editBlock = $('#edit-block');
    const sugTable = $('#sug-table');

    $('#btn-correct').click((e) => {
        e.preventDefault();
        correct();
    });

    function correct() {
        const content = contentBlock.val().trim();

        if (!content) return;

        $.ajax({
            type: "POST",
            headers: {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            url: "http://nlp-jedi.cs.nthu.edu.tw:1314/correct",
            // url: "http://nlp-ultron.cs.nthu.edu.tw:1315/",
            contentType: 'application/json; charset=UTF-8',
            data: JSON.stringify({
                'content': content
            }),
            dataType: "json",
            success: showEdit,
        });
    }


    const rightPtn = /(\{\+(.*?)\+\})/gm;
    const warningPtn = /(\\\*(.*?)\*\\)/gm;
    const wrongPtn = /(\[-(.*?)-\])/gm;

    function showEdit(data) {
        console.log(data);
        let { edit, suggestions = undefined } = data;

        edit = edit.replace('\n', '<br>')
            .replace(rightPtn, "<span class='text-success'>$2</span>")
            .replace(wrongPtn, "<span class='text-danger'>$2</span>")
            .replace(warningPtn, "<span class='text-warning'>$2</span>");
        editBlock.html(edit);

        if (!suggestions) return;

        const sugList = suggestions.reduce((prev, curr, idx) => {
            const { category, tk, bef, aft, ngram } = curr;
            const textStyle = category === 'wrong' ? 'text-danger' : 'text-warning';
            return prev + `<tr>
            <th scope="row" class="${textStyle}">${tk}</th>
            <td>${bef}</td><td>${aft}</td><td>${ngram}</td>
            </tr>`;
        }, '')
        sugTable.html(sugList);

    }
})