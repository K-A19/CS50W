document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);
  document.querySelector('#compose-form').onsubmit = send_email;

  // By default, load the inbox
  load_mailbox('inbox');
});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';
  document.querySelector('#view-email').style.display = 'none';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';

}

function send_email() {

  // Make a request to send the email
  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
        recipients: document.querySelector('#compose-recipients').value,
        subject: document.querySelector('#compose-subject').value,
        body: document.querySelector('#compose-body').value
    })
  })
  .then(response => response.json())
  .then(result => {

      // Checks if the email was sent successfully
      if (result.message !== undefined) {

          // Redirects the uder to their sent mailbox
          load_mailbox('sent');

          // Displays confirmation that the message was sent successfully
          alert(result.message);

          // Prints a success message to the console
          console.log('Success, Email sent');

      }
      else {

          // Prints the error to the console
          console.log('Error:', result.error);

          // Displays the error message for the user
          document.querySelector('#message').innerHTML = result.error;
      }
  })
  .catch(error => {

      // Prints the error to the console
      console.log('Error:', error);

      // Displays the error message for the user
      document.querySelector('#message').innerHTML = error;

  });

  // Prevents form submission
  return false;

}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#view-email').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  // Makes a request to get the emails in that mailbox
  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
      
    for (let email in emails) {

        // Creates a new list item and changes the text it contains
        let element = document.createElement('li');
        element.innerHTML = `<span class='bold'>${emails[email].subject}</span><span>Sent by <span class='bold'>${emails[email].sender}</span> at <span class='bold'>${emails[email].timestamp}</span></span>`;

        // Sets the class of the lsit item to change how its design
        element.className = 'list-group-item';

        // Sets the background colour on the email item depending on if it is read or not
        if (emails[email].read) {
            element.style.backgroundColor = 'lightgray';
        }
        else {
            element.style.backgroundColor = 'white';
        }
        
        // Opens the email in expanded form when it is clicked on
        element.onclick = () => view_email(emails[email].id);

        // Adds the email item to the current mailbox
        document.querySelector('#emails-view').append(element);
    };

      
  })
  .catch(error => {

    // Prints the error to the console
    console.log('Error:', error);

    // Displays the error message for the user
    document.querySelector('#message').innerHTML = error;
  });
}


function view_email(id) {
  
  // Show the view-email view and hides all other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#view-email').style.display = 'block';

  fetch(`/emails/${id}`)
  .then(response => response.json())
  .then(email => {

      // Changes the label of the button depending on whether or not the email is alreayd archived
      if (email.archived) {
        document.querySelector("#archive").innerHTML = 'Unarchive';
      }
      else {
        document.querySelector("#archive").innerHTML = 'Archive';
      }

      // Adds an event listener to the button to be able to toggle whether or not the email is archived
      document.querySelector("#archive").onclick = () => archive(id, !email.archived);

      // Displays informationn about the email
      document.querySelector("#view_sender").innerHTML = email.sender;
      document.querySelector("#view_recipients").innerHTML = email.recipients;
      document.querySelector("#view_subject").innerHTML = email.subject;
      document.querySelector("#view_timestamp").innerHTML = email.timestamp;
      document.querySelector("#view_body").innerHTML = email.body;


      // Allows the reply button to allow for replies
      document.querySelector('#reply').onclick = () => reply(email.sender, email.subject, email.timestamp, email.body);

  })
  .catch(error => {

    // Prints the error to the console
    console.log('Error:', error);

    // Displays the error message for the user
    document.querySelector('#message').innerHTML = error;

    // Breaks the function
    return false;
  });

  // Marks the email as read after we are sure the email's data was displayed properly
  fetch(`/emails/${id}`, {
    method: 'PUT',
    body: JSON.stringify({
        read: true
    })
  });

}


function archive(id, action) {

  // Changes whether the email is archived or not
  fetch(`/emails/${id}`, {
    method: 'PUT',
    body: JSON.stringify({
        archived: action
    })
  })
  .then(function () {
    // Redirects the user to their inbox once the promise changing the archiving is complete
    load_mailbox('inbox');
    console.log('Archive change successful');

  });

}


function reply(recipient, subject, timestamp, original_body) {
  
  // Loads the basic compose view first
  compose_email()

  // Changes the original email sender to the recipient
  document.querySelector('#compose-recipients').value = recipient;

  // Decides whether or not 'Re: ' must be added infront of the subject
  if (subject.split(' ', 1)[0] == "Re:") {
    document.querySelector('#compose-subject').value = subject;
  }
  else {
    document.querySelector('#compose-subject').value = `Re: ${subject}`;
  }

  // Populated the textarea with content form the original email
  document.querySelector('#compose-body').value = `On ${timestamp} ${recipient} wrote:\n${original_body}\n\n`;
  document.querySelector('#compose-body').focus()
}