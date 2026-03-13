$(document).ready(function() {
    const chatWindow = $("#chatWindow");

    function loadMessages() {
        $.get("/messages", function(data) {
            chatWindow.empty();
            data.forEach(msg => {
                let bubbleClass = msg.is_jom ? "jom" : "user";
                let content = "";
                if (msg.file_type === "image") {
                    content = `<img src="${msg.file_url}" style="max-width:150px; display:block;">`;
                } else if (msg.file_type === "file") {
                    content = `<a href="${msg.file_url}" target="_blank">Download File</a>`;
                }
                content = msg.message ? msg.message + "<br>" + content : content;
                let avatar = msg.is_jom ? '<img class="avatar" src="/static/jom.jpg">' : '';
                chatWindow.append(`<div class="message ${bubbleClass}">${avatar}<strong>${msg.username} (${msg.timestamp}):</strong> ${content}</div>`);
            });
            chatWindow.scrollTop(chatWindow[0].scrollHeight);
        });
    }

    loadMessages();
    setInterval(loadMessages, 1000);

    $("#chatForm").submit(function(e) {
        e.preventDefault();
        let formData = new FormData();
        formData.append("username", $("#username").val());
        formData.append("message", $("#message").val());
        let file = $("#fileInput")[0].files[0];
        if (file) formData.append("file", file);

        $.ajax({
            url: "/chat",
            type: "POST",
            data: formData,
            contentType: false,
            processData: false,
            success: function() {
                $("#message").val("");
                $("#fileInput").val("");
                loadMessages();
            }
        });
    });

    $("#themeSelector").change(function() {
        $("body").removeClass().addClass(`theme-${$(this).val()}`);
    });
});