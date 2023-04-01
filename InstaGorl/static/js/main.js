function upvote(event, postId) {
    event.preventDefault();
    if (document.getElementById('user_authenticated').value === 'True') {
        const upvoteButton = document.getElementById(`upvote-button-${postId}`);
        const downvoteButton = document.getElementById(`downvote-button-${postId}`);
        const voteCount = document.getElementById(`votes-count-${postId}`);
        const csrfToken = document.getElementsByName('csrfmiddlewaretoken')[0].value;

        fetch(`/upvote/${postId}`, {
            method: "POST",
            headers: {
                "X-CSRFToken": csrfToken,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                "upvoted": !upvoteButton.classList.contains("voted"),
                "downvoted": downvoteButton.classList.contains("voted"),
            })
        })
        .then((response) => response.json())
        .then((data) => {
            voteCount.innerHTML = data.score;
            if (data.upvoted) {
                upvoteButton.classList.add("voted");
                downvoteButton.classList.remove("voted");
            } else {
                downvoteButton.classList.remove("voted");
            }
        })
        .catch((error) => {
            console.error(error);
            alert("Could not upvote post.");
        });
    } else {
        window.location.replace('/login/?next=' + '&message=You must be logged in to upvote a post Gorl!');
    }
}




function downvote(event, postId) {
    event.preventDefault();
    if (document.getElementById('user_authenticated').value === 'True') {
        const upvoteButton = document.getElementById(`upvote-button-${postId}`);
        const downvoteButton = document.getElementById(`downvote-button-${postId}`);
        const voteCount = document.getElementById(`votes-count-${postId}`);
        const csrfToken = document.getElementsByName('csrfmiddlewaretoken')[0].value;

        fetch(`/downvote/${postId}`, {
            method: "POST",
            headers: {
                "X-CSRFToken": csrfToken,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                "upvoted": upvoteButton.classList.contains("voted"),
                "downvoted": !downvoteButton.classList.contains("voted"),
            })
        })
        .then((response) => response.json())
        .then((data) => {
            voteCount.innerHTML = data.score;
            if (data.downvoted) {
                upvoteButton.classList.remove("voted");
                downvoteButton.classList.add("voted");
            } else {
                downvoteButton.classList.remove("voted");
            }
        })
        .catch((error) => {
            console.error(error);
            alert("Could not downvote post.");
        });
    } else {
        window.location.replace('/login/?next=' + '&message=You must be logged in to downvote a post Gorl!');
    }
}


document.addEventListener("DOMContentLoaded", function() {
    var select = document.getElementById("posts-per-page-select");
    var selectedValue = getCookiePost("posts_per_page");
    if(selectedValue){
        select.value = selectedValue;
    }
    select.addEventListener("change", function() {
        var selectedValue = select.options[select.selectedIndex].value;
        //store the selected value in a cookie
        document.cookie = "posts_per_page=" + selectedValue;
        //reload the page
        location.reload();
    });

    function getCookiePost(name) {
        var value = "; " + document.cookie;
        var parts = value.split("; " + name + "=");
        if (parts.length == 2) return parts.pop().split(";").shift();
    }
});


document.addEventListener("DOMContentLoaded", function() {
    var select = document.getElementById("posts-per-page-selectt");
    var selectedValue = getCookieUserPost("posts_per_pagee");
    if(selectedValue){
        select.value = selectedValue;
    }
    select.addEventListener("change", function() {
        var selectedValue = select.options[select.selectedIndex].value;
        //store the selected value in a cookie
        document.cookie = "posts_per_pagee=" + selectedValue;
        //reload the page
        location.reload();
    });

    function getCookieUserPost(name) {
        var value = "; " + document.cookie;
        var parts = value.split("; " + name + "=");
        if (parts.length == 2) return parts.pop().split(";").shift();
    }
});


document.addEventListener("DOMContentLoaded", function() {
    var select = document.getElementById("posts-per-page-selecttt");
    var selectedValue = getCookieSearchPost("posts_per_pageee");
    if(selectedValue){
        select.value = selectedValue;
    }
    select.addEventListener("change", function() {
        var selectedValue = select.options[select.selectedIndex].value;
        //store the selected value in a cookie
        document.cookie = "posts_per_pageee=" + selectedValue;
        //reload the page
        location.reload();
    });

    function getCookieSearchPost(name) {
        var value = "; " + document.cookie;
        var parts = value.split("; " + name + "=");
        if (parts.length == 2) return parts.pop().split(";").shift();
    }
});


document.addEventListener("DOMContentLoaded", function() {
    var select = document.getElementById("posts-per-page-selectttt");
    var selectedValue = getCookieSearchUser("posts_per_pageeee");
    if(selectedValue){
        select.value = selectedValue;
    }
    select.addEventListener("change", function() {
        var selectedValue = select.options[select.selectedIndex].value;
        //store the selected value in a cookie
        document.cookie = "posts_per_pageeee=" + selectedValue;
        //reload the page
        location.reload();
    });

    function getCookieSearchUser(name) {
        var value = "; " + document.cookie;
        var parts = value.split("; " + name + "=");
        if (parts.length == 2) return parts.pop().split(";").shift();
    }
});

const readMoreLinks = document.querySelectorAll(".read-more");

for (let i = 0; i < readMoreLinks.length; i++) {
  readMoreLinks[i].classList.add("like-button");

  readMoreLinks[i].addEventListener("click", function(e) {
    e.preventDefault();
    const body = document.querySelector(`#body_${this.dataset.id}`);
    if (this.textContent === "...Read more") {
      body.innerHTML = this.dataset.fullText;
      this.textContent = "...Read less";
    } else {
      body.innerHTML = this.dataset.truncatedText;
      this.textContent = "...Read more";
    }
  });
}


const dropArea = document.getElementById('drop-area');
const fileInput = document.getElementById('id_files');

fileInput.addEventListener('change', handleFileInputChange);
dropArea.addEventListener('dragenter', handleDragEnter);
dropArea.addEventListener('dragleave', handleDragLeave);
dropArea.addEventListener('dragover', handleDragOver);
dropArea.addEventListener('drop', handleFileDrop);

function handleFileInputChange(e) {
  updateFileLabel(e.target.files[0].name);
  dropArea.classList.remove('bg-light');
  dropArea.classList.add('bg-suc');
}

function handleDragEnter(e) {
  e.preventDefault();
  dropArea.classList.remove('bg-suc');
  dropArea.classList.add('bg-light');
}

function handleDragLeave(e) {
  e.preventDefault();
  dropArea.classList.remove('bg-light');
}

function handleDragOver(e) {
  e.preventDefault();
  dropArea.classList.add('bg-light');
}

function handleFileDrop(e) {
  e.preventDefault();
  if (e.dataTransfer.files.length > 0) {
    const file = e.dataTransfer.files[0];
    fileInput.files = e.dataTransfer.files;
    updateFileLabel(file.name);
    dropArea.classList.remove('bg-light');
    dropArea.classList.add('bg-suc');
  }
}

function updateFileLabel(fileName) {
  fileLabel.innerText = fileName;
}


// Create a function to remove the error message
function removeErrorMessage() {
    var errorDiv = document.querySelector(".comment-error-message");
    if (errorDiv) {
        errorDiv.remove();
    }
}



function postComment(postId) {
    var csrftoken = $("[name=csrfmiddlewaretoken]").val();
    var content = document.getElementById("comment").value;
    var url = $('#comment-form').data('url');

    $.ajax({
        type: "POST",
        url: url,
        headers: { "X-CSRFToken": csrftoken },
        data: { "post_id": postId, "content": content },
        success: function (response) {
            document.getElementById("comment-form").reset();

            // Check if there was an error message in the response
            if (response.success === false) {
                // Display the error message
                var errorDiv = document.createElement("div");
                errorDiv.innerHTML = response.error_message;
                errorDiv.classList.add("comment-error-message");
                errorDiv.style.color = "hotpink";
                var commentsDiv = document.getElementById("comments");
                commentsDiv.appendChild(errorDiv);

                // Remove the error message after 30 seconds
                setTimeout(removeErrorMessage, 30000);
            } else {
                // Create the new comment
                var commentsDiv = document.getElementById("comments");
                var newCommentDiv = document.createElement("div");
                newCommentDiv.setAttribute('id', 'comment-' + response.comment_id);
                newCommentDiv.innerHTML = response.new_comment;
                newCommentDiv.dataset.commentId = response.comment_id;

                // Set upvote/downvote status
                if (response.upvoted) {
                    newCommentDiv.querySelector('.upvote-comment-button').classList.add("voted");
                }
                if (response.downvoted) {
                    newCommentDiv.querySelector('.downvote-comment-button').classList.add("voted");
                }

                // Update new comment score
                if (response.new_comment_score) {
                    newCommentDiv.querySelector('.comment-votes-count').innerHTML = response.new_comment_score;
                }

                // Attach event listeners to the upvote and downvote buttons in the new comment
                var upvoteButton = newCommentDiv.querySelector('.upvote-comment-button');
                var downvoteButton = newCommentDiv.querySelector('.downvote-comment-button');
                var voteCount = newCommentDiv.querySelector('.comment-votes-count');
                var commentId = newCommentDiv.dataset.commentId;

                // Add event listeners for upvote and downvote buttons
                upvoteButton.addEventListener('click', function(event) {
                    upvoteNewComment(event, commentId);
                });
                downvoteButton.addEventListener('click', function(event) {
                    downvoteNewComment(event, commentId);
                });

                // Add necessary data attributes for upvote/downvote buttons
                upvoteButton.setAttribute('data-upvoted', response.upvoted);
                upvoteButton.setAttribute('data-downvoted', response.downvoted);
                downvoteButton.setAttribute('data-upvoted', response.upvoted);
                downvoteButton.setAttribute('data-downvoted', response.downvoted);

                // Add the new comment to the existing comments
                commentsDiv.appendChild(newCommentDiv);

                // Update new comment score
                if (response.new_comment_score) {
                    var newCommentScore = commentsDiv.querySelector('#comment-' + response.comment_id + ' .comment-votes-count');
                    if (newCommentScore) {
                        newCommentScore.innerHTML = response.new_comment_score;
                    }
                }
            }
        },

        error: function (response) {
            console.log(response);
        }
    });
}







function upvoteComment(event, commentId) {
    event.preventDefault();
    if (document.getElementById('user_authenticated').value === 'True') {
        const upvoteButton = document.getElementById(`upvote-comment-button-${commentId}`);
        const downvoteButton = document.getElementById(`downvote-comment-button-${commentId}`);
        const voteCount = document.getElementById(`comment-votes-count-${commentId}`);
        const csrfToken = document.getElementsByName('csrfmiddlewaretoken')[0].value;

        fetch(`/comment/upvote/${commentId}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": csrfToken,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                "upvoted": !upvoteButton.classList.contains("voted"),
                "downvoted": downvoteButton.classList.contains("voted"),
            })
        })
        .then((response) => response.json())
        .then((data) => {
            if (voteCount) {
                voteCount.innerHTML = data.score;
            }
            if (data.upvoted) {
                upvoteButton.classList.add("voted");
                downvoteButton.classList.remove("voted");
            } else {
                downvoteButton.classList.remove("voted");
            }
        })
        .catch((error) => {
            console.error(error);
            alert("Could not upvote comment.");
        });
    } else {
        window.location.replace('/login/?next=' + '&message=You must be logged in to upvote a comment Gorl!');
    }
}

function downvoteComment(event, commentId) {
    event.preventDefault();
    if (document.getElementById('user_authenticated').value === 'True') {
        const upvoteButton = document.getElementById(`upvote-comment-button-${commentId}`);
        const downvoteButton = document.getElementById(`downvote-comment-button-${commentId}`);
        const voteCount = document.getElementById(`comment-votes-count-${commentId}`);
        const csrfToken = document.getElementsByName('csrfmiddlewaretoken')[0].value;

        fetch(`/comment/downvote/${commentId}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": csrfToken,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                "upvoted": upvoteButton.classList.contains("voted"),
                "downvoted": !downvoteButton.classList.contains("voted"),
            })
        })
        .then((response) => response.json())
        .then((data) => {
            if (voteCount) {
                voteCount.innerHTML = data.score;
            }
            if (data.downvoted) {
                upvoteButton.classList.remove("voted");
                downvoteButton.classList.add("voted");
            } else {
                downvoteButton.classList.remove("voted");
            }
        })
        .catch((error) => {
            console.error(error);
            alert("Could not downvote comment.");
        });
    } else {
        window.location.replace('/login/?next=' + '&message=You must be logged in to downvote a comment Gorl!');
    }
}



function upvoteNewComment(event, commentId) {
    event.preventDefault();
    if (document.getElementById('user_authenticated').value === 'True') {
        const upvoteButton = document.getElementById(`upvote-comment-button-${commentId}`);
        const downvoteButton = document.getElementById(`downvote-comment-button-${commentId}`);
        const voteCount = document.getElementById(`comment-${commentId}`).querySelector('.comment-votes-count');
        const csrfToken = document.getElementsByName('csrfmiddlewaretoken')[0].value;

        fetch(`/comment/upvote/${commentId}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": csrfToken,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                "upvoted": !upvoteButton.classList.contains("voted"),
                "downvoted": downvoteButton.classList.contains("voted"),
            })
        })
        .then((response) => response.json())
        .then((data) => {
            if (voteCount) {
                voteCount.innerHTML = data.score;
            }
            if (data.upvoted) {
                upvoteButton.classList.add("voted");
                downvoteButton.classList.remove("voted");
            } else {
                downvoteButton.classList.remove("voted");
            }
        })
        .catch((error) => {
            console.error(error);
            alert("Could not upvote comment.");
        });
    } else {
        window.location.replace('/login/?next=' + '&message=You must be logged in to upvote a comment Gorl!');
    }
}

function downvoteNewComment(event, commentId) {
    event.preventDefault();
    if (document.getElementById('user_authenticated').value === 'True') {
        const upvoteButton = document.getElementById(`upvote-comment-button-${commentId}`);
        const downvoteButton = document.getElementById(`downvote-comment-button-${commentId}`);
        const voteCount = document.getElementById(`comment-${commentId}`).querySelector('.comment-votes-count');
        const csrfToken = document.getElementsByName('csrfmiddlewaretoken')[0].value;

        fetch(`/comment/downvote/${commentId}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": csrfToken,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                "upvoted": upvoteButton.classList.contains("voted"),
                "downvoted": !downvoteButton.classList.contains("voted"),
            })
        })
        .then((response) => response.json())
        .then((data) => {
            if (voteCount) {
                voteCount.innerHTML = data.score;
            }
            if (data.downvoted) {
                upvoteButton.classList.remove("voted");
                downvoteButton.classList.add("voted");
            } else {
                downvoteButton.classList.remove("voted");
            }
        })
        .catch((error) => {
            console.error(error);
            alert("Could not downvote comment.");
        });
    } else {
        window.location.replace('/login/?next=' + '&message=You must be logged in to downvote a comment Gorl!');
    }
}







function postCommentComment(commentId, parent_id) {
    var csrftoken = $("[name=csrfmiddlewaretoken]").val();
    var content = document.getElementById("commentReply").value;
    var url = $('#commentReply-form').data('url');

    $.ajax({
        type: "POST",
        url: url,
        headers: { "X-CSRFToken": csrftoken },
        data: { "comment_id": commentId, "content": content, "parent_id": parent_id },
        success: function (response) {
            document.getElementById("commentReply-form").reset();

            // Check if there was an error message in the response
            if (response.success === false) {
                // Display the error message
                var errorDiv = document.createElement("div");
                errorDiv.innerHTML = response.error_message;
                errorDiv.classList.add("comment-error-message");
                errorDiv.style.color = "hotpink";
                var commentsDiv = document.getElementById("commentsReply");
                commentsDiv.appendChild(errorDiv);

                // Remove the error message after 30 seconds
                setTimeout(removeErrorMessage, 30000);
            } else {
                // Create the new comment
                var commentsDiv = document.getElementById("commentsReply");
                var newCommentDiv = document.createElement("div");
                newCommentDiv.setAttribute('id', 'comment-' + response.comment_id);
                newCommentDiv.innerHTML = response.new_comment;
                newCommentDiv.dataset.commentId = response.comment_id;

                // Set upvote/downvote status
                if (response.upvoted) {
                    newCommentDiv.querySelector('.upvote-comment-button').classList.add("voted");
                }
                if (response.downvoted) {
                    newCommentDiv.querySelector('.downvote-comment-button').classList.add("voted");
                }

                // Update new comment score
                if (response.new_comment_score) {
                    newCommentDiv.querySelector('.comment-votes-count').innerHTML = response.new_comment_score;
                }

                // Attach event listeners to the upvote and downvote buttons in the new comment
                var upvoteButton = newCommentDiv.querySelector('.upvote-comment-button');
                var downvoteButton = newCommentDiv.querySelector('.downvote-comment-button');
                var voteCount = newCommentDiv.querySelector('.comment-votes-count');
                var commentId = newCommentDiv.dataset.commentId;

                // // Add event listeners for upvote and downvote buttons
                // upvoteButton.addEventListener('click', function(event) {
                //     upvoteNewComment(event, commentId, parent_id);
                // });
                // downvoteButton.addEventListener('click', function(event) {
                //     downvoteNewComment(event, commentId, parent_id;
                // });

                // // Add necessary data attributes for upvote/downvote buttons
                // upvoteButton.setAttribute('data-upvoted', response.upvoted);
                // upvoteButton.setAttribute('data-downvoted', response.downvoted);
                // downvoteButton.setAttribute('data-upvoted', response.upvoted);
                // downvoteButton.setAttribute('data-downvoted', response.downvoted);

                // Add the new comment to the existing comments
                commentsDiv.appendChild(newCommentDiv);

                // Update the comments section with the new comment
                var commentsSection = $('#commentsReply');
                var commentsSectionHtml = commentsSection.html();
                commentsSectionHtml += newCommentDiv.outerHTML;
                commentsSection.html(commentsSectionHtml);

                // Update new comment score
                if (response.new_comment_score) {
                    var newCommentScore = commentsDiv.querySelector('#comment-' + response.comment_id + ' .comment-votes-count');
                    if (newCommentScore) {
                        newCommentScore.innerHTML = response.new_comment_score;
                    }
                }
            }
        },

        error: function (response) {
            console.log(response);
        }
    });
}
