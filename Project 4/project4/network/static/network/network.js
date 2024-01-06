// Ensures the DOM is loaded before allowing events to occur
document.addEventListener('DOMContentLoaded', function() {

    // Adds event listeners to each edit button for when they are clicked
    document.querySelectorAll('.edit').forEach(function(element) {
        element.addEventListener('click', function() { 
            // Passes on the id of the edit button clicked which matches the id of the post to be edited
            edit_post(this.id);
        });
    });

});

// Edits the post without reloading the page by makin JSON requests
function edit_post(id) {

    // Makes all edit buttons disappear so the user can only edit one thing at a time
    document.querySelectorAll('.edit').forEach(function(element) {
        element.style.visibility = "hidden";
        element.disabled = true;
    });

    // Gets the content of the message the user wants to edit
    fetch(`/post/${id}`)
    .then(response => response.json())
    .then(post => {

        // Changes the main body of the post to a textarea for editing and a save button 
        edit_space = document.getElementsByClassName(`card-text ${id}`)[0];
        edit_space.innerHTML = `<label for="content_edit">Edit Content of Post:</label><br><textarea style="width:100%" rows="5" id="content_edit" name="content_edit">${post.content}</textarea><br><div class="left-align"><button class= "btn btn-dark" id="save_edit">Save</button></div>`;
        content = document.querySelector("#content_edit");
        console.log(content);

         // Saves the post when the save button has been clicked
        document.querySelector("#save_edit").addEventListener('click', () => save_edit(id, content.value));


    })
    .catch(error => {

        // Prints the error to the console
        console.log('Error:', error);
    
        // Displays the error message for the user
        document.querySelector('.center_message').innerHTML = error;
    
        // Breaks the function
        return false;
    });

}

// Saves the new content of a post and makes sure edit butotns are back to visible and the post has its new content
function save_edit(id, content) {

    console.log("Saving")
    // Saves the post with its new content
    fetch(`/post/${id}`, {
        method: 'PUT',
        body: JSON.stringify({
            content : content
        })
    })
    .then( function(){

        // Changed the main body of the post to the new content rather than having it as a textarea for editing
        document.getElementsByClassName(`card-text ${id}`)[0].innerHTML = content;

        // Makes all the edit buttons reappear for use again
        document.querySelectorAll('.edit').forEach(function(element) {
            element.style.visibility = "visible";
            element.disabled = false;
        });

    });
}