import { AnsiUp } from './ansi_up.js'

$(function() {
    $("#sortable").sortable();
    $("#sortable").disableSelection();
});

function executeOrderOne() {
    var order = $('#sortable').sortable('toArray', {attribute: 'data-id'});
    $.ajax({
        url: '/execute',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({order: order}),
        success: function(response) {
            console.log(response);
            //do something here
        }
    });
}

function executeLS() {
    $.ajax({
        url: '/execute_ls',
        type: 'GET',
        success: function(response) {
            $('#terminal').html(response.output.replace(/\n/g, '<br>')); // Replace newlines with <br> for HTML display
        }
    });
}

// event listener
$(document).on('click', '.special-class', executeLS);

document.addEventListener('DOMContentLoaded', function () {
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    socket.on('connect', function() {
        socket.emit('client_connected', {data: 'I\'m connected!'});
    });
    socket.on('update_output', function(msg) {
        document.getElementById('terminal').innerHTML = msg.data.replace(/\n/g, '<br>');
    });
});

$(function() {
    $("#sortable").sortable();
    $("#sortable").disableSelection();
});

function executeOrder() {
    var order = $('#sortable').sortable('toArray', {attribute: 'data-id'});
    $.ajax({
        url: '/execute',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({order: order}),
        success: function(response) {
            console.log(response);
        }
    });
}

let outputBuffer = [];
let updateInterval = 500;

function flushOutputBuffer() {
    const terminal = $('#terminal');
    terminal.append(outputBuffer.join('') + '<br>');
    //terminal.scrollTop(terminal.prop('scrollHeight'));
    outputBuffer = [];
}

setInterval(flushOutputBuffer, updateInterval);

// Socket.IO
var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

socket.on('connect', function() {
    //emit a message upon connection if needed
    console.log('Websocket connected!');
});

function ansiToHtml(ansiText) {
    var ansiUp = new AnsiUp();
    var html = ansiUp.ansi_to_html(ansiText);
    return html;
}

$(document).on('click', '.button-1', function() {
    $.ajax({
        url: '/execute-airodump', //
        type: 'POST',
        success: function(response) {
            var terminal = $('#terminal');
            var htmlOutput = ansiToHtml(response);
            terminal.html(htmlOutput.replace(/\n/g, '<br>'));
            //terminal.scrollTop(terminal.prop("scrollHeight"));
        },
        error: function(xhr, status, error) {
            console.log("Error: " + error);
        }
    });
});

$(document).on('click', '.button-3', function() {
    $.ajax({
        url: '/device-info', //
        type: 'POST',
        success: function(response) {
            var terminal = $('#terminal');
            var htmlOutput = ansiToHtml(response);
            terminal.html(htmlOutput.replace(/\n/g, '<br>'));
            //terminal.scrollTop(terminal.prop("scrollHeight"));
        },
        error: function(xhr, status, error) {
            console.log("Error: " + error);
        }
    });
});

$(document).on('click', '.button-4', function() {
    $.ajax({
        url: '/get-connected-devices',
        type: 'POST',
        success: function(response) {
            var terminal = $('#terminal');
            var htmlOutput = ansiToHtml(response);
            terminal.html(htmlOutput.replace(/\n/g, '<br>'));
            //terminal.scrollTop(terminal.prop("scrollHeight"));
        },
        error: function(xhr, status, error) {
            console.log("Error: " + error);
        }
    });
});


$(document).ready(function() {
    $('#clear-terminal').click(function() {
        socket.emit('stop_output');
        $('#terminal').html(''); // clear output
    });
});


function prepareContentColumn() {
    const contentColumn = document.getElementById('content-column');
    contentColumn.style.display = 'block'; // Ensure it's visible
    contentColumn.innerHTML = ''; // Clear previous contents
    // Add the message div back in
    const messageDiv = document.createElement('div');
    messageDiv.id = 'message';
    messageDiv.textContent = 'Scanned Information';
    contentColumn.appendChild(messageDiv);
}

document.querySelector('.button-4').addEventListener('click', function() {
    document.getElementById('content-column').style.display = 'block';

    fetch('/get-connected-devices', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        const dropdown = document.getElementById('dynamic-dropdown');
        dropdown.innerHTML = '';
        data.forEach(device => {
            const option = document.createElement('option');
            option.value = device;
            option.textContent = device;
            dropdown.appendChild(option);
        });

        let submitButton = document.getElementById('submit-button');
        if (!submitButton) {
            submitButton = document.createElement('button');
            submitButton.id = 'submit-button';
            submitButton.textContent = 'Submit';
            document.getElementById('content-column').appendChild(submitButton);

            submitButton.addEventListener('click', function() {
                const selectedDevice = dropdown.value;
                fetch('/start-deauth', { // todo replace
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ selectedDevice: selectedDevice })
                })
                .then(response => {
                    if (response.ok) {
                        return response.json();
                    }
                    throw new Error('Network response was not ok.');
                })
                .then(data => {
                    console.log('Success:', data);
                })
                .catch((error) => {
                    console.error('Error:', error);
                });
            });
        }
    })
    .catch(error => {
        console.error('Error fetching connected devices:', error);
    });
});


// $(document).on('click', '.button-2', function (){
//     $('#message').html('Scanned Access Points');
//
//     $.getJSON('/router-info', function (data) {
//         var dropdown = $('#dynamic-dropdown');
//         dropdown.empty();
//         $.each(data.options, function(key, entry){
//             dropdown.append($('<option></option>').attr('value', entry.id).text(entry.text));
//         });
//     });
//     $('#content-column').show();
// });

$(document).on('click', '.button-2', function (){
    $('#message').html('Scanned Access Points');
    $.ajax({
        url: '/get-ap-info',
        type: 'GET',
        dataType: 'json',
        success: function(data) {
            var dropdown = $('#dynamic-dropdown');
            dropdown.empty();

            data.forEach(function(ap, index) {
                var bssid = ap[0];
                var pwr = ap[1];
                var channel = ap[2];
                var ssid = ap[3];

                var optionText = `Option ${index + 1}: BSSID ${bssid} - PWR: ${pwr}, CH: ${channel}, SSID: ${ssid}`;
                dropdown.append($('<option></option>').attr('value', bssid).text(optionText));
            });
        },
        error: function(xhr, status, error) {
            console.log("Error fetching AP info: " + error);
        }
    });
    $('#content-column').show();
});
